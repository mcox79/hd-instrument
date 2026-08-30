"""Belief-timeline CI-separated proof on construction gold (isolates the ToM x TIME composition).

Arms (all decoded on the substrate's OWN FHRR organs via belief_partition codes + binding + cleanup):
  timeline            -- the per-agent sample-and-hold belief timeline (the mechanism)
  current_belief      -- STRONGEST FLOOR: timeline-agnostic current belief (latest observed value,
                         SAME observation cue, NO reading-time axis)
  narration_timeline  -- same sample-and-hold but ordered by NARRATION not the register's chronology
                         (isolates the temporal-order register on the flashback subset)
  omniscient          -- answer belief from reality (the false-belief deficit)
  always_initial      -- answer the initial placement always
  twin                -- INFO-FREE: shuffle the event/observation ORDER (destroys latest-observed<=t)
  empty               -- no events registered (degenerate control)
  repB_tempctx        -- the swept FHRR temporal-context representation (measured, expected lossy)

Headline: belief-question accuracy (belief + false_belief) of the timeline vs the current-belief
floor, CI-separated, with the twin's null p95 below it. Positive control = the belief queries the
current-belief floor CANNOT get (belief-at-t != final-observed). Reality/memory are intact controls.
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
    SubstrateReadout, TemporalContextBeliefRegister, make_answerer,
    timeline_belief, current_belief_floor, reality_at, initial_value, hindsight_invariant,
)
from experiments.belief_timeline_gold import generate_gold, gold_stats, LOCATIONS

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_query_v1")


def _vocab_for(scen):
    """Value vocabulary for cleanup = the locations that appear plus a few distractors."""
    present = sorted({e.value for e in scen.events})
    extra = [l for l in LOCATIONS if l not in present][:4]
    return present + extra


def _answer_query(arm, ans_fn, readout, scen, q, vocab):
    """Return (pred, correct) for a single query, decoding on-substrate."""
    a, obj, t, typ = q["agent"], q["obj"], q["t"], q["type"]
    if typ == "belief":
        pred = ans_fn(a, obj, t)
        return pred, int(pred == q["gold"])
    if typ == "false_belief":
        bel = ans_fn(a, obj, t)
        rea = readout.readout(obj, reality_at(scen.events, obj, t), vocab)
        pred_fb = bool(bel is not None and bel != rea)
        return pred_fb, int(pred_fb == q["gold"])
    if typ == "reality":
        pred = readout.readout(obj, reality_at(scen.events, obj, t), vocab)
        return pred, int(pred == q["gold"])
    if typ == "memory":
        pred = readout.readout(obj, initial_value(scen.events, obj), vocab)
        return pred, int(pred == q["gold"])
    raise ValueError(typ)


def _boot_ci(correct, n_boot=2000, seed=0):
    """Bootstrap 95% CI of the mean of a 0/1 vector (resample items)."""
    correct = np.asarray(correct, dtype=float)
    if len(correct) == 0:
        return (0.0, 0.0, 0.0)
    rng = np.random.default_rng(seed)
    means = [correct[rng.integers(0, len(correct), len(correct))].mean() for _ in range(n_boot)]
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(correct.mean()), float(lo), float(hi)


def run(mode="full", d=1024, seed=20260829, n_scen=60, twin_seeds=200):
    scens = generate_gold(n=(20 if mode == "smoke" else n_scen), seed=seed)
    readout = SubstrateReadout(d=d, seed=seed)

    # per-arm collection of correctness, tagged by query type + scenario tags + a "discriminating" flag
    arms = ["timeline", "current_belief", "narration_timeline", "omniscient", "always_initial",
            "empty", "repB_tempctx"]
    records = {arm: [] for arm in arms}

    for scen in scens:
        vocab = _vocab_for(scen)
        repB = TemporalContextBeliefRegister(d=d, seed=seed)
        for a in scen.agents:
            repB.build(a, scen.events, scen.observed)
        answerers = {arm: make_answerer(arm, scen, vocab, readout, seed=seed, repB=repB)
                     for arm in arms}
        for q in scen.queries:
            # is this belief query one the current-belief floor cannot get? (positive control)
            disc = False
            if q["type"] in ("belief", "false_belief"):
                fl_bel = current_belief_floor(scen.events, scen.observed, q["agent"], q["obj"], q["t"])
                tl_bel = timeline_belief(scen.events, scen.observed, q["agent"], q["obj"], q["t"])
                disc = (fl_bel != tl_bel)
            for arm in arms:
                pred, ok = _answer_query(arm, answerers[arm], readout, scen, q, vocab)
                records[arm].append({"type": q["type"], "tags": scen.tags, "disc": disc, "ok": ok})

    def acc(arm, pred=lambda r: True):
        v = [r["ok"] for r in records[arm] if pred(r)]
        return _boot_ci(v, seed=seed), len(v)

    belief_q = lambda r: r["type"] in ("belief", "false_belief")
    disc_q = lambda r: r["type"] in ("belief", "false_belief") and r["disc"]
    control_q = lambda r: r["type"] in ("reality", "memory")

    results = {}
    for arm in arms:
        (m, lo, hi), n = acc(arm, belief_q)
        results[arm] = {"belief_acc": m, "ci": [lo, hi], "n": n}

    # positive control: the subset the current-belief floor cannot get
    pos = {}
    for arm in ("timeline", "current_belief", "narration_timeline"):
        (m, lo, hi), n = acc(arm, disc_q)
        pos[arm] = {"acc": m, "ci": [lo, hi], "n": n}

    # controls (shared across arms): reality + memory on the timeline arm
    (cm, clo, chi), cn = acc("timeline", control_q)

    # info-free twin over many order-shuffle seeds -> null distribution
    twin_accs = []
    for ts in range(twin_seeds if mode != "smoke" else 40):
        vv = []
        for scen in scens:
            vocab = _vocab_for(scen)
            ans = make_answerer("twin", scen, vocab, readout, seed=ts)
            for q in scen.queries:
                if q["type"] not in ("belief", "false_belief"):
                    continue
                _, ok = _answer_query("twin", ans, readout, scen, q, vocab)
                vv.append(ok)
        twin_accs.append(float(np.mean(vv)))
    twin_mean = float(np.mean(twin_accs))
    twin_p95 = float(np.percentile(twin_accs, 95))

    # distance robustness: belief accuracy by (final_chrono - floor(t)) on MULTI_CHANGE queries
    dist_bins = {}
    for scen in scens:
        if "multi_change" not in scen.tags:
            continue
        vocab = _vocab_for(scen)
        tl = make_answerer("timeline", scen, vocab, readout, seed=seed, repB=None)
        fl = make_answerer("current_belief", scen, vocab, readout, seed=seed, repB=None)
        final_ch = max(e.chrono for e in scen.events)
        for q in scen.queries:
            if q["type"] != "belief":
                continue
            dist = int(final_ch - int(q["t"]))  # events between the query and the story end
            b = dist_bins.setdefault(dist, {"timeline": [], "current_belief": []})
            b["timeline"].append(int(tl(q["agent"], q["obj"], q["t"]) == q["gold"]))
            b["current_belief"].append(int(fl(q["agent"], q["obj"], q["t"]) == q["gold"]))
    distance = {str(k): {"timeline": float(np.mean(v["timeline"])),
                         "current_belief": float(np.mean(v["current_belief"])),
                         "n": len(v["timeline"])}
                for k, v in sorted(dist_bins.items())}

    # DECOUPLING / anti-hindsight control (research drill #1): a later UNOBSERVED world change must
    # NOT shift "what A believed at T". A clean store is invariant (beats the brain's curse-of-
    # knowledge); a reconstruct-with-leak (the omniscient arm) would shift.
    inv_ok = inv_n = 0
    leak_omniscient = 0
    for scen in scens:
        for q in scen.queries:
            if q["type"] != "belief":
                continue
            r = hindsight_invariant(scen.events, scen.observed, q["agent"], q["obj"], q["t"])
            if r is None:
                continue
            inv_n += 1
            inv_ok += int(r)
            # would an omniscient (reality-reading) reader shift? it answers reality_at(t), which is
            # unaffected by a LATER event, so construct the contrast at the belief level: the leak an
            # omniscient reader shows is that its answer already IGNORES observation (measured above);
            # here we count that the timeline's past answer != reality (i.e. a leak WOULD corrupt it).
            if timeline_belief(scen.events, scen.observed, q["agent"], q["obj"], q["t"]) != \
               reality_at(scen.events, q["obj"], q["t"]):
                leak_omniscient += 1
    hindsight = {"invariant_fraction": (inv_ok / inv_n if inv_n else None), "n": inv_n,
                 "belief_differs_from_reality_at_risk": leak_omniscient}

    # REP B timescale stress (research drill Q3): the graded temporal-context read is accurate when
    # events are well-separated but should degrade as the inter-event GAP shrinks (contiguity
    # crosstalk / order-uncertainty near boundaries), while the discrete sample-and-hold (rep A)
    # stays exact. This maps the regime where discrete beats graded -- the honest representation sweep.
    from experiments.belief_timeline import WorldEvent as _WE, Scenario as _Sc
    repB_stress = {}
    for dt in (2.0, 1.0, 0.5, 0.25, 0.1):
        a_ok = b_ok = ntot = 0
        for si in range(12):
            locs = [f"loc{si}_{k}" for k in range(4)]
            events = [_WE("obj", locs[k], chrono=k * dt, narr=k, kind="initial" if k == 0 else "move")
                      for k in range(4)]
            observed = {("A", k * dt): True for k in range(4)}
            vocab = locs + ["dloc1", "dloc2"]
            sc = _Sc(f"stress_{dt}_{si}", ["A"], events, observed, [])
            repB = TemporalContextBeliefRegister(d=d, seed=seed)
            for k in range(4):
                tq = k * dt + dt * 0.5      # query mid-gap after event k
                gold = timeline_belief(events, observed, "A", "obj", tq)
                a = SubstrateReadout(d=d, seed=seed).readout("obj", gold, vocab)  # rep A read-out
                b = repB.belief("A", "obj", tq, events, observed, vocab)          # rep B graded read
                a_ok += int(a == gold)
                b_ok += int(b == gold)
                ntot += 1
        repB_stress[str(dt)] = {"repA": a_ok / ntot, "repB": b_ok / ntot, "n": ntot}

    metrics = {
        "mode": mode, "d": d, "seed": seed,
        "gold": gold_stats(scens),
        "repB_timescale_stress": repB_stress,
        "arms": results,
        "positive_control_floor_cannot_get": pos,
        "controls_reality_memory": {"acc": cm, "ci": [clo, chi], "n": cn},
        "twin": {"mean": twin_mean, "p95": twin_p95, "n_seeds": len(twin_accs)},
        "distance_robustness": distance,
        "hindsight_decoupling": hindsight,
        "headline": {
            "timeline": results["timeline"]["belief_acc"],
            "timeline_ci": results["timeline"]["ci"],
            "floor_current_belief": results["current_belief"]["belief_acc"],
            "floor_ci": results["current_belief"]["ci"],
            "twin_p95": twin_p95,
            "ci_separated": results["timeline"]["ci"][0] > results["current_belief"]["ci"][1],
            "beats_twin": results["timeline"]["ci"][0] > twin_p95,
        },
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full", choices=["smoke", "full"])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--d", type=int, default=1024)
    args = ap.parse_args()
    if args.self_test:
        m = run(mode="smoke", d=512, twin_seeds=20)
        assert m["headline"]["timeline"] > 0.9, m["headline"]
        print("self-test PASS", json.dumps(m["headline"], indent=2))
        return
    m = run(mode=args.mode, d=args.d)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    h = m["headline"]
    print("=" * 78)
    print("BELIEF TIMELINE -- construction gold (ToM x TIME composition)")
    print("=" * 78)
    print(f"gold: {m['gold']['n_scenarios']} scenarios, {m['gold']['n_queries']} queries "
          f"({m['gold']['n_belief']} belief)")
    print(f"  TIMELINE belief-acc      {h['timeline']:.3f}  CI {h['timeline_ci']}")
    print(f"  FLOOR (current-belief)   {h['floor_current_belief']:.3f}  CI {h['floor_ci']}")
    print(f"  info-free TWIN p95       {h['twin_p95']:.3f}")
    for arm in ("narration_timeline", "omniscient", "always_initial", "empty", "repB_tempctx"):
        r = m["arms"][arm]
        print(f"  [{arm:20s}]        {r['belief_acc']:.3f}  CI {r['ci']}")
    pc = m["positive_control_floor_cannot_get"]
    print(f"  POSITIVE CONTROL (floor-cannot-get subset, n={pc['timeline']['n']}): "
          f"timeline {pc['timeline']['acc']:.3f} vs current-belief {pc['current_belief']['acc']:.3f}")
    cc = m["controls_reality_memory"]
    print(f"  reality+memory controls  {cc['acc']:.3f}  CI {cc['ci']}  (n={cc['n']})")
    print(f"  CI-SEPARATED over floor: {h['ci_separated']}   BEATS TWIN p95: {h['beats_twin']}")
    hs = m["hindsight_decoupling"]
    print(f"  HINDSIGHT-DECOUPLING: past belief invariant to later unobserved change "
          f"{hs['invariant_fraction']} (n={hs['n']})  [clean store beats curse-of-knowledge]")
    print(f"  distance robustness: {json.dumps(m['distance_robustness'])}")
    print(f"  repB timescale stress (repA vs repB by inter-event gap): "
          f"{json.dumps(m['repB_timescale_stress'])}")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
