"""CAUSAL-NETWORK EDGE TYPER (the discourse level): type each CROSS-EVENT causal edge
CAUSE / ENABLE / PREVENT by composing the landed Wolff force-dynamic typer over the
Trabasso event network, validated CI-separated over the connective/adjacency PLACEHOLDER
(which links but cannot type), with BOTH info-free twins LOSING and the lift ISOLATED
from single-clause typing.  (problem: causation_is_typed_per_clause_not_across_the_causal_network)

WHAT THIS ADDS OVER THE SINGLE-CLAUSE TYPER (causation_has_no_force_dynamic_typing, integrated):
  The landed typer types ONE clause (a single agent/verb/patient/outcome). Most narrative
  causation is a CROSS-SENTENCE event->event link with no single causal verb:
      "The dam broke. The village flooded."   (CAUSE, two separate events)
      "The levee blocked the surge. The town stayed dry."   (PREVENT -- the flood NEVER happened)
  This cell builds the EDGE typer: construct the causal network (edges by force/connective/
  bridge NECESSITY + temporal PRECEDENCE), then TYPE each edge by composing the force typer over
  the TWO linked events -- the AFFECTOR force class from the CAUSE event's verb, the endstate
  polarity read from the EFFECT event's clause (a DIFFERENT Trabasso node).

BRAIN MECHANISM (PINNED -- Trabasso & van den Broek 1985; Trabasso & Sperry 1985; Wolff 2007):
  the discourse CAUSAL NETWORK -- events are nodes; a causal edge exists where the earlier
  event is "necessary in the circumstances" for the later; edge DIRECTION is gated by temporal
  precedence (cause precedes effect -- the integrated TIME register / past-perfect flashback).
  Force dynamics LABELS each edge CAUSE/ENABLE/PREVENT (Wolff's truth-table, now over the two
  linked events' force configuration rather than one clause's verb). OUR-SYNTHESIS: Trabasso
  gives the network, Wolff gives edge labels; their COMPOSITION is not one published result.
  OUR-INVENTION-UNDER-TEST (swept, not adopted): the edge-construction NECESSITY rule (force /
  connective / bridge evidence, NOT adjacency) and the (clause-pair -> affector/endstate) mapping.

THE ISOLATION (bar sec.3): the cross-event contribution is the EFFECT-CLAUSE endstate reading.
  A prevention whose success is only stated in the effect clause ("...the town stayed dry")
  CANNOT be typed from the cause clause alone -- the single-clause typer reads the cause clause's
  own (default-reached) polarity and mistypes the prevented edge. The PERCLAUSE ablation
  (endstate from the CAUSE clause) measures exactly this: it recovers CAUSE/ENABLE/SEQUENTIAL but
  LOSES the PREVENT class, which is the measured cross-event lift.

EXTRACTION IS GIVEN as structured events (verb-lemma + clause tokens + tense), exactly as the
landed single-clause typer's construction gold gives (agent, verb, patient) to isolate the
mechanism. The TESTED components are (a) network CONSTRUCTION (which events link, direction via
precedence, existence via necessity), (b) the endstate/negation read from the EFFECT clause, and
(c) the force typing. Self-extraction on RAW real prose + its coverage bound is the sibling cell
exp_causal_network_realtext_v1. Glass-box, NO external LLM: the FrameNet force lexicon is a static
nltk asset reused verbatim from the landed _force_dynamics_lexicon. ASCII-only. Deterministic.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
import traceback
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._force_dynamics_lexicon import (  # noqa: E402
    build_force_lexicon, force_dynamic_type, detect_endstate_reached,
)

ANCHOR = "causal_network_edge_typer_v1"
N_BOOT = 5000
N_SHUF = 300
SEED = 20260830
LABELS = ("CAUSE", "ENABLE", "PREVENT", "SEQUENTIAL")

# Causal connectives (a network-construction cue; our gold is connective-NEUTRAL so a connective
# baseline is blind, but the necessity rule still licenses an edge on one when present).
CONNECTIVES = {"so", "therefore", "thus", "hence", "because", "since", "consequently"}


# ---------------------------------------------------------------------------
# GOLD -- connective-neutral CROSS-SENTENCE passages as STRUCTURED events (extraction GIVEN).
# Each event: E(verb_lemma, "clause text", tense in {NOW, PRIOR}). tense=PRIOR == past-perfect
# ("had Ved") -> the TIME register places it BEFORE narrative-now events regardless of text order.
# The arm gets the events + the OUTCOME index; it must FIND the cause (precedence + necessity) and
# TYPE the edge. The endstate is READ from the effect clause tokens by the glass-box detector.
# Cause verbs are covered by the FrameNet force lexicon (built independently, not hand-added).
# ---------------------------------------------------------------------------
def E(v, clause, tense="NOW"):
    return {"v": v, "clause": clause.split(), "tense": tense}


def _it(subset, events, outcome, gold, note=""):
    return dict(subset=subset, events=events, outcome=outcome, gold=gold, note=note)


# CAUSE: cause verb is CAUSE-class; effect endstate REACHED (no negation cue in the effect clause).
SET_CAUSE = [
    _it("CAUSE", [E("topple", "the storm toppled the oak"), E("crush", "the trunk crushed the fence")], 1, "CAUSE"),
    _it("CAUSE", [E("ignite", "a spark ignited the hay"), E("burn", "the whole barn burned down")], 1, "CAUSE"),
    _it("CAUSE", [E("shatter", "the hammer shattered the vase"), E("scatter", "the pieces flew across the floor")], 1, "CAUSE"),
    _it("CAUSE", [E("swell", "the flood swelled the river"), E("overflow", "the banks overflowed by dawn")], 1, "CAUSE"),
    _it("CAUSE", [E("crack", "the quake cracked the wall"), E("collapse", "the ceiling fell onto the desks")], 1, "CAUSE"),
    _it("CAUSE", [E("break", "the blast broke the window"), E("rain", "the glass rained onto the street")], 1, "CAUSE"),
    _it("CAUSE", [E("melt", "the fire melted the ice"), E("rush", "the water rushed down the valley")], 1, "CAUSE"),
    _it("CAUSE", [E("weaken", "the current weakened the hull"), E("sink", "the old ship sank at once")], 1, "CAUSE"),
    _it("CAUSE", [E("snap", "the gale snapped the mast"), E("crash", "the sail came down hard")], 1, "CAUSE"),
    _it("CAUSE", [E("burn", "the blaze burned the rope"), E("fall", "the bridge dropped into the gorge")], 1, "CAUSE"),
]

# ENABLE: cause verb is a LETTING verb (release/free/let/allow/permit/enable/loosen); effect tends
# and is REACHED.
SET_ENABLE = [
    _it("ENABLE", [E("release", "the guard released the prisoner"), E("walk", "the man went out the gate")], 1, "ENABLE"),
    _it("ENABLE", [E("let", "the warden let the crowd in"), E("surge", "the people rushed toward the stands")], 1, "ENABLE"),
    _it("ENABLE", [E("allow", "the clerk allowed the guest inside"), E("enter", "the visitor came into the hall")], 1, "ENABLE"),
    _it("ENABLE", [E("permit", "the pass permitted the trader through"), E("cross", "the trader went over the border")], 1, "ENABLE"),
    _it("ENABLE", [E("enable", "the law enabled the worker to vote"), E("cast", "she put her ballot in at noon")], 1, "ENABLE"),
    _it("ENABLE", [E("free", "the sailor freed the boat"), E("drift", "the vessel moved out to sea")], 1, "ENABLE"),
    _it("ENABLE", [E("loosen", "the thaw loosened the soil"), E("push", "the seedlings came up overnight")], 1, "ENABLE"),
    _it("ENABLE", [E("release", "the keeper released the hawk"), E("soar", "the bird rose over the ridge")], 1, "ENABLE"),
    _it("ENABLE", [E("permit", "the captain permitted shore leave"), E("scatter", "the sailors went into the town")], 1, "ENABLE"),
    _it("ENABLE", [E("allow", "the steward allowed the servants out"), E("rest", "they lay down until the bell")], 1, "ENABLE"),
]

# PREVENT: cause verb is a PREVENT verb whose surface is an OPPOSING ACTION, not an outcome-negation
# (hold/halt/shield/deter/restrain/save/guard/curb/protect/defend -- deliberately NOT block/stop/
# prevent, whose past-tense surface is itself a not-reached cue the single-clause typer already reads).
# The prevention's SUCCESS is stated ONLY in the EFFECT clause (a negation/safety cue) -> the genuine
# cross-event killer: the cause clause alone cannot tell a succeeded from a failed prevention.
SET_PREVENT = [
    _it("PREVENT", [E("hold", "the sandbags held the river"), E("reach", "no water reached the door")], 1, "PREVENT"),
    _it("PREVENT", [E("halt", "the wall halted the flames"), E("remain", "the house was spared entirely")], 1, "PREVENT"),
    _it("PREVENT", [E("shield", "the guard shielded the boy"), E("remain", "the child was unharmed")], 1, "PREVENT"),
    _it("PREVENT", [E("deter", "the guards deterred the raiders"), E("come", "the village was safe by morning")], 1, "PREVENT"),
    _it("PREVENT", [E("restrain", "the dam restrained the torrent"), E("flood", "the valley was intact")], 1, "PREVENT"),
    _it("PREVENT", [E("save", "the rope saved the climber"), E("fall", "she did not fall to the rocks")], 1, "PREVENT"),
    _it("PREVENT", [E("guard", "the moat guarded the keep"), E("enter", "no enemy entered the walls")], 1, "PREVENT"),
    _it("PREVENT", [E("curb", "the tax curbed the spending"), E("grow", "the deficit was averted")], 1, "PREVENT"),
    _it("PREVENT", [E("protect", "the vaccine protected the child"), E("come", "the fever never came")], 1, "PREVENT"),
    _it("PREVENT", [E("defend", "the shield defended the knight"), E("strike", "the blow was avoided")], 1, "PREVENT"),
]

# SEQUENTIAL: cause verb is a NON-force verb, no connective -> no causal necessity -> NO edge.
# The placeholder links anyway (a false-positive causal link); the network typer abstains.
SET_SEQ = [
    _it("SEQUENTIAL", [E("pour", "she poured the coffee"), E("yawn", "he yawned at the table")], 1, "SEQUENTIAL"),
    _it("SEQUENTIAL", [E("gleam", "the lamp gleamed in the hall"), E("gather", "the guests gathered slowly")], 1, "SEQUENTIAL"),
    _it("SEQUENTIAL", [E("chime", "the clock chimed the hour"), E("stretch", "the old cat stretched")], 1, "SEQUENTIAL"),
    _it("SEQUENTIAL", [E("close", "he closed the heavy book"), E("flicker", "the candle flickered once")], 1, "SEQUENTIAL"),
    _it("SEQUENTIAL", [E("sweep", "the maid swept the floor"), E("rise", "the morning sun climbed higher")], 1, "SEQUENTIAL"),
    _it("SEQUENTIAL", [E("sing", "the bird sang at dawn"), E("roll", "a cart went down the lane")], 1, "SEQUENTIAL"),
    _it("SEQUENTIAL", [E("read", "the boy read the letter"), E("hum", "his sister hummed a tune")], 1, "SEQUENTIAL"),
    _it("SEQUENTIAL", [E("walk", "the farmer walked the road"), E("drift", "the clouds moved east")], 1, "SEQUENTIAL"),
    _it("SEQUENTIAL", [E("gaze", "she gazed at the linen"), E("whistle", "the kettle sang in the kitchen")], 1, "SEQUENTIAL"),
    _it("SEQUENTIAL", [E("watch", "he watched the river"), E("wade", "a heron stepped near the reeds")], 1, "SEQUENTIAL"),
]

# CHAIN (cause != most-recent): a 3-event passage with a DEAD-END (non-force) event between cause
# and effect. The true cause jumps back over the intervening event; a most-recent baseline mislinks
# to the dead-end (non-force -> wrong type). Outcome is the final event.
SET_CHAIN = [
    _it("CHAIN", [E("ignite", "the spark ignited the hay"), E("bark", "a dog barked in the yard"),
                  E("burn", "the barn burned down")], 2, "CAUSE"),
    _it("CHAIN", [E("release", "the guard released the hound"), E("glow", "a lamp glowed somewhere"),
                  E("bolt", "the deer ran away")], 2, "ENABLE"),
    _it("CHAIN", [E("shield", "the wall shielded the cottage"), E("shout", "someone shouted an order"),
                  E("stay", "the cottage stayed safe")], 2, "PREVENT"),
    _it("CHAIN", [E("crack", "the blast cracked the dam"), E("wail", "a siren wailed loudly"),
                  E("flood", "the town went under by noon")], 2, "CAUSE"),
    _it("CHAIN", [E("free", "the keeper freed the birds"), E("laugh", "a child laughed nearby"),
                  E("scatter", "they rose into the sky")], 2, "ENABLE"),
    _it("CHAIN", [E("hold", "the sandbags held the tide"), E("cry", "a gull cried overhead"),
                  E("remain", "the pier was intact")], 2, "PREVENT"),
    _it("CHAIN", [E("topple", "the storm toppled the tree"), E("whinny", "a horse whinnied in fear"),
                  E("crush", "the cart was smashed flat")], 2, "CAUSE"),
    _it("CHAIN", [E("deter", "the lock deterred the thief"), E("loom", "a shadow loomed upstairs"),
                  E("occur", "no theft happened that night")], 2, "PREVENT"),
]

# FLASHBACK (precedence positive control): the CAUSE is stated AFTER the effect in past perfect
# (tense=PRIOR). Text-adjacency finds no prior cause; the precedence gate recovers it. Scored on
# CAUSE-IDENTIFICATION (did the arm find the right cause event?) -- the direction-gate discriminator.
SET_FLASHBACK = [
    _it("FLASHBACK", [E("flood", "the village flooded that spring"), E("break", "the old dam had broken", "PRIOR")], 0, "CAUSE"),
    _it("FLASHBACK", [E("walk", "the prisoner walked free at last"), E("release", "the guard had released him", "PRIOR")], 0, "ENABLE"),
    _it("FLASHBACK", [E("burn", "the barn burned to ashes"), E("ignite", "a spark had ignited the hay", "PRIOR")], 0, "CAUSE"),
    _it("FLASHBACK", [E("stay", "the town was spared the fire"), E("block", "the wall had blocked the flames", "PRIOR")], 0, "PREVENT"),
    _it("FLASHBACK", [E("sink", "the ship sank before noon"), E("weaken", "the current had weakened the hull", "PRIOR")], 0, "CAUSE"),
    _it("FLASHBACK", [E("surge", "the crowd surged inside"), E("let", "the warden had let them through", "PRIOR")], 0, "ENABLE"),
]

TYPING_POOL = SET_CAUSE + SET_ENABLE + SET_PREVENT + SET_SEQ + SET_CHAIN


# ---------------------------------------------------------------------------
# Network construction over GIVEN events (indices = text order; tense PRIOR = flashback).
# ---------------------------------------------------------------------------
def _precedes(events, j, outcome):
    """Event j causally precedes the outcome i: earlier in text OR a past-perfect (PRIOR) event
    anywhere (the TIME register), and not the outcome itself."""
    if j == outcome:
        return False
    if events[j]["tense"] == "PRIOR" and events[outcome]["tense"] != "PRIOR":
        return True
    return j < outcome


def find_cause_placeholder(events, outcome):
    """The connective/adjacency PLACEHOLDER: most-recent event strictly before the outcome in TEXT
    order (locality). Blind to flashback; always links when a prior event exists."""
    prior = [j for j in range(len(events)) if j < outcome]
    return prior[-1] if prior else None


def find_cause_net(events, outcome, lexicon):
    """Precedence-gated, NECESSITY-licensed cause finder. Candidates = events that causally precede
    the outcome. License an edge only on force-dynamic / connective / bridge evidence (NOT bare
    adjacency): prefer the NEAREST force-class cause verb; else a connective; else a force-action
    bridge. Returns (cause_index_or_None, licensed_bool)."""
    cand = [j for j in range(len(events)) if _precedes(events, j, outcome)]
    force = [j for j in cand if lexicon.get(events[j]["v"]) is not None]
    if force:
        # nearest in the causal ordering: PRIOR events, then by text index
        return max(force, key=lambda j: (events[j]["tense"] != "PRIOR", j)), True
    # explicit connective anywhere in the outcome clause or a candidate clause
    for j in cand:
        if any(w in CONNECTIVES for w in events[outcome]["clause"] + events[j]["clause"]):
            return j, True
    return None, False   # no necessity evidence -> NO causal edge (abstain)


# ---------------------------------------------------------------------------
# Edge typers (the arms). Each returns (label, info).
# ---------------------------------------------------------------------------
def _fold(t):
    return t if t in ("CAUSE", "ENABLE", "PREVENT") else "SEQUENTIAL"


def arm_net_typer(item, lexicon):
    """MECHANISM: precedence/necessity-licensed edge + force typing with endstate read from the
    EFFECT clause (cross-event)."""
    events, outcome = item["events"], item["outcome"]
    c, licensed = find_cause_net(events, outcome, lexicon)
    if not licensed or c is None:
        return "SEQUENTIAL", {"cause": None, "reason": "no_necessity"}
    es = detect_endstate_reached(events[outcome]["clause"])       # <-- EFFECT clause (cross-event)
    t = force_dynamic_type(events[c]["v"], es, lexicon)
    return _fold(t), {"cause": events[c]["v"], "endstate_reached": es, "raw": t}


def arm_perclause(item, lexicon):
    """ISOLATION ablation (bar sec.3): SAME cause event as the network, but endstate read from the
    CAUSE clause (single-clause style). Cannot see a prevention whose success is stated only in the
    effect clause -> loses the PREVENT class."""
    events, outcome = item["events"], item["outcome"]
    c, licensed = find_cause_net(events, outcome, lexicon)
    if not licensed or c is None:
        return "SEQUENTIAL", {"cause": None}
    es = detect_endstate_reached(events[c]["clause"])            # <-- CAUSE clause (single-clause)
    t = force_dynamic_type(events[c]["v"], es, lexicon)
    return _fold(t), {"cause": events[c]["v"], "endstate_reached": es}


def arm_placeholder(item, majority="CAUSE", **kw):
    """The connective/adjacency PLACEHOLDER: LINKS cause->outcome (adjacency) but is TYPE-BLIND ->
    asserts the majority causal type for every linked pair, and never abstains (false-positive link
    on non-causal sequence)."""
    return majority, {}


# ---------------------------------------------------------------------------
# Scoring / bootstrap / twins.
# ---------------------------------------------------------------------------
def score(items, arm_fn, **kw):
    return [int(arm_fn(it, **kw)[0] == it["gold"]) for it in items]


def _acc(recs):
    return sum(recs) / len(recs) if recs else 0.0


def _boot(recs, seed=SEED, n=N_BOOT):
    if not recs:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    m = len(recs)
    b = sorted(sum(recs[rng.randrange(m)] for _ in range(m)) / m for _ in range(n))
    return sum(recs) / m, b[int(0.025 * n)], b[int(0.975 * n)]


def _shuffled_lexicon(lexicon, seed):
    """Info-free twin A: permute the force-class VALUES across the verb KEYS (destroys verb->force
    semantics, preserves the class marginal)."""
    rng = random.Random(seed)
    keys = list(lexicon.keys())
    vals = list(lexicon.values())
    rng.shuffle(vals)
    return dict(zip(keys, vals))


def _edge_type_shuffle_acc(items, preds, seed):
    """Info-free twin B: permute the arm's PREDICTED types across items (destroys the type->item
    assignment; preserves the predicted-type marginal)."""
    rng = random.Random(seed)
    p = list(preds)
    rng.shuffle(p)
    return sum(int(p[i] == items[i]["gold"]) for i in range(len(items))) / len(items)


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def self_test():
    lex = build_force_lexicon()
    assert arm_net_typer(SET_CAUSE[0], lex)[0] == "CAUSE", "toppled -> crushed = CAUSE"
    assert arm_net_typer(SET_PREVENT[0], lex)[0] == "PREVENT", "blocked surge -> stayed dry = PREVENT"
    assert arm_perclause(SET_PREVENT[0], lex)[0] != "PREVENT", "per-clause cannot see the effect-clause block"
    assert arm_net_typer(SET_ENABLE[0], lex)[0] == "ENABLE", "released -> walked free = ENABLE"
    assert arm_net_typer(SET_SEQ[0], lex)[0] == "SEQUENTIAL", "poured/yawned = no causal edge"
    assert arm_net_typer(SET_CHAIN[2], lex)[0] == "PREVENT", "blocked...(shout)...stayed safe = PREVENT"
    # precedence: the flashback cause (PRIOR) is found though it is later in text
    c, lic = find_cause_net(SET_FLASHBACK[0]["events"], 0, lex)
    assert lic and SET_FLASHBACK[0]["events"][c]["v"] == "break", "precedence finds the past-perfect cause"
    assert find_cause_placeholder(SET_FLASHBACK[0]["events"], 0) is None, "adjacency finds no prior cause"
    print("[self-test] PASS")
    return True


def _flashback_cause_id(lex):
    net_ok = adj_ok = 0
    detail = []
    for it in SET_FLASHBACK:
        events, outcome = it["events"], it["outcome"]
        gold_cause = it["events"][1]["v"] if len(it["events"]) > 1 else None
        # gold cause is the PRIOR event
        gold_cause = next(events[j]["v"] for j in range(len(events)) if events[j]["tense"] == "PRIOR")
        nc, lic = find_cause_net(events, outcome, lex)
        ac = find_cause_placeholder(events, outcome)
        n_ok = lic and nc is not None and events[nc]["v"] == gold_cause
        a_ok = ac is not None and events[ac]["v"] == gold_cause
        net_ok += int(n_ok)
        adj_ok += int(a_ok)
        detail.append({"gold_cause": gold_cause,
                       "net": None if nc is None else events[nc]["v"],
                       "adj": None if ac is None else events[ac]["v"]})
    n = len(SET_FLASHBACK)
    return {"n": n, "precedence_cause_id_acc": round(net_ok / n, 4),
            "adjacency_cause_id_acc": round(adj_ok / n, 4), "detail": detail}


def main():
    out_dir = _out_dir()
    t0 = time.perf_counter()
    lex = build_force_lexicon()

    preds_net = [arm_net_typer(it, lex)[0] for it in TYPING_POOL]
    preds_pc = [arm_perclause(it, lex)[0] for it in TYPING_POOL]
    preds_ph = [arm_placeholder(it)[0] for it in TYPING_POOL]
    golds = [it["gold"] for it in TYPING_POOL]

    rec_net = [int(p == y) for p, y in zip(preds_net, golds)]
    rec_pc = [int(p == y) for p, y in zip(preds_pc, golds)]
    rec_ph = [int(p == y) for p, y in zip(preds_ph, golds)]

    m_net, lo_net, hi_net = _boot(rec_net)
    m_pc, lo_pc, hi_pc = _boot(rec_pc)
    m_ph, lo_ph, hi_ph = _boot(rec_ph)

    # info-free twin A: force-class shuffle
    twinA = sorted(_acc([int(arm_net_typer(it, _shuffled_lexicon(lex, 1000 + s))[0] == it["gold"])
                         for it in TYPING_POOL]) for s in range(N_SHUF))
    twinA_mean, twinA_p95 = sum(twinA) / len(twinA), twinA[int(0.95 * (len(twinA) - 1))]

    # info-free twin B: edge-type shuffle
    twinB = sorted(_edge_type_shuffle_acc(TYPING_POOL, preds_net, 2000 + s) for s in range(N_SHUF))
    twinB_mean, twinB_p95 = sum(twinB) / len(twinB), twinB[int(0.95 * (len(twinB) - 1))]

    per_subset = {}
    for name, items in [("CAUSE", SET_CAUSE), ("ENABLE", SET_ENABLE), ("PREVENT", SET_PREVENT),
                        ("SEQUENTIAL", SET_SEQ), ("CHAIN", SET_CHAIN)]:
        per_subset[name] = {"n": len(items),
                            "net": round(_acc(score(items, arm_net_typer, lexicon=lex)), 4),
                            "perclause": round(_acc(score(items, arm_perclause, lexicon=lex)), 4),
                            "placeholder": round(_acc(score(items, arm_placeholder)), 4)}

    flash = _flashback_cause_id(lex)

    beats_placeholder = lo_net > hi_ph
    beats_perclause = lo_net > hi_pc
    twinA_loses = lo_net > twinA_p95
    twinB_loses = lo_net > twinB_p95
    precedence_gate = flash["precedence_cause_id_acc"] > flash["adjacency_cause_id_acc"]
    passed = (beats_placeholder and beats_perclause and twinA_loses and twinB_loses)
    verdict = ("CAUSAL_NETWORK_EDGE_TYPER_CI_SEPARATED_OVER_PLACEHOLDER_AND_PERCLAUSE__TWINS_LOSE"
               if passed else "EDGE_TYPER_DID_NOT_CLEAR_ALL_GATES")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "summary": (
            f"CAUSAL-NETWORK EDGE TYPER (cross-sentence, extraction given): pooled 4-way edge-type acc NET "
            f"{m_net:.3f} [{lo_net:.3f},{hi_net:.3f}] (hw {(hi_net-lo_net)/2:.3f}) vs PLACEHOLDER (type-blind "
            f"majority) {m_ph:.3f} [{lo_ph:.3f},{hi_ph:.3f}] (beats={beats_placeholder}) and vs PERCLAUSE "
            f"ablation (endstate from cause clause) {m_pc:.3f} [{lo_pc:.3f},{hi_pc:.3f}] (beats={beats_perclause} "
            f"-- the cross-event PREVENT lift). Force-class-shuffle twin {twinA_mean:.3f} (p95 {twinA_p95:.3f}, "
            f"loses={twinA_loses}); edge-type-shuffle twin {twinB_mean:.3f} (p95 {twinB_p95:.3f}, "
            f"loses={twinB_loses}). PREVENT subset NET {per_subset['PREVENT']['net']:.3f} / perclause "
            f"{per_subset['PREVENT']['perclause']:.3f} / placeholder {per_subset['PREVENT']['placeholder']:.3f}. "
            f"Flashback precedence cause-ID {flash['precedence_cause_id_acc']:.3f} vs adjacency "
            f"{flash['adjacency_cause_id_acc']:.3f} (precedence_gate={precedence_gate})."),
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "n_pool": len(TYPING_POOL),
        "pooled": {
            "net_acc": round(m_net, 4), "net_ci": [round(lo_net, 4), round(hi_net, 4)],
            "net_ci_halfwidth": round((hi_net - lo_net) / 2, 4),
            "perclause_acc": round(m_pc, 4), "perclause_ci": [round(lo_pc, 4), round(hi_pc, 4)],
            "placeholder_acc": round(m_ph, 4), "placeholder_ci": [round(lo_ph, 4), round(hi_ph, 4)],
        },
        "twin_force_class_shuffle": {"mean": round(twinA_mean, 4), "p95": round(twinA_p95, 4),
                                     "loses": twinA_loses, "n_shuffles": N_SHUF},
        "twin_edge_type_shuffle": {"mean": round(twinB_mean, 4), "p95": round(twinB_p95, 4),
                                   "loses": twinB_loses, "n_shuffles": N_SHUF},
        "per_subset": per_subset,
        "flashback_precedence_control": flash,
        "gates": {"beats_placeholder_ci": beats_placeholder, "beats_perclause_ci": beats_perclause,
                  "force_shuffle_twin_loses": twinA_loses, "edge_shuffle_twin_loses": twinB_loses,
                  "precedence_gate": precedence_gate},
        "isolation_note": (
            "PREVENT is the measured CROSS-EVENT lift: NET reads the endstate from the EFFECT clause "
            "('...stayed dry'/'no water reached'), so it types a prevented edge; PERCLAUSE reads the CAUSE "
            "clause (default reached) and mistypes it (NO_CAUSATION->SEQUENTIAL). CAUSE/ENABLE/SEQUENTIAL do "
            "not separate NET from PERCLAUSE; PREVENT does. PLACEHOLDER (majority CAUSE) also fails "
            "ENABLE/PREVENT/SEQUENTIAL -- it cannot type at all, and false-links non-causal sequence."),
        "brain_note": (
            "Trabasso & van den Broek 1985 causal network (events=nodes, edges='necessary in the "
            "circumstances'); Wolff 2007 force dynamics LABELS each edge; precedence gates direction (TIME "
            "register / past-perfect). Composition is OUR-SYNTHESIS; edge-construction necessity + clause-pair "
            "mapping are OUR-INVENTION-UNDER-TEST. Glass-box, no LLM."),
        "scope": (
            "Constructed connective-neutral CROSS-SENTENCE passages; extraction GIVEN as structured events "
            "(verb-lemma + clause tokens + tense), as the landed single-clause typer's gold gives (agent, verb, "
            "patient). TESTED: network construction (precedence + necessity), effect-clause endstate read, force "
            "typing. FrameNet force lexicon built before this gold. Self-extraction on RAW real prose + coverage "
            "bound is the sibling cell exp_causal_network_realtext_v1."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"[verdict] {verdict}")
    print(f"elapsed={elapsed:.2f}s -> {os.path.join(out_dir, 'metrics.json')}")
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        _atomic_write(_out_dir(), {"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                                   "traceback": traceback.format_exc()[:4000]})
        raise
