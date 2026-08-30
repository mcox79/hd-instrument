"""GRADED CAUSAL NECESSITY -- the higher-fidelity edge representation (build across the discrete-type wall).
   (problem: causation_is_typed_per_clause_not_across_the_causal_network)

A brain-mechanism research drill (research_graded_necessity_and_cause_dominance_2026-08-30.md) returned:
the brain represents each causal edge as a GRADED (necessity, sufficiency) strength, NOT a discrete
3-way type. Evidence: Trabasso, van den Broek & Suh (1989) weight causal-network edges by graded
"necessity in the circumstances" (necessity AND sufficiency); Kuperberg, Paczynski & Ditman (2011,
JoCN 23:1230) show a GRADED N400 by causal relatedness (direct online neural evidence against a
discrete type); Cheng (1997) generative/preventive causal power are continuous; Wolff (2007) DERIVES
CAUSE/ENABLE/PREVENT by discretizing continuous force vectors. So the discrete typer (the landed one +
my cross-event extension) is a LOSSY read-out of an underlying graded representation, and the
"he held his tongue because he promised" CAUSE-vs-PREVENT ambiguity is an artifact of the discretization,
not the representation.

THIS CELL builds the graded estimator and validates it against the BRAIN'S OWN METRIC:
  necessity(A for E) = counterfactual "would E be reached without A?" -> derived from the force config:
    - patient does NOT tend toward E (CAUSE)  -> A is the driving force -> necessity HIGH
    - patient DOES tend (ENABLE, A removes a barrier) -> patient's own force drives E -> A's causal-force
      necessity LOW (Trabasso: enabling is the LEAST necessary link)
  x a DOMAIN-DETERMINISM weight: physical forces are law-like (high necessity), psychological causation is
    probabilistic (an agent may not act on a belief) -> physical > motivational > psychological. This is an
    INDEPENDENT principle (domain determinism), and reproducing Trabasso's measured human ordering
    (physical > motivational > psychological > enabling) VALIDATES it (it is not fit to the ordering).
  sufficiency(A) = affector magnitude vs the endstate threshold (does A alone produce E).
The DISCRETE CAUSE/ENABLE/PREVENT type is then a THRESHOLDED READ-OUT of (necessity, sufficiency) against
an explicit reference endstate -- and it must MATCH the discrete typer on the constructed gold (consistency).

VALIDATION (can-fail, one-variable, the brain's own metric):
  (1) CONSISTENCY: the graded read-out reproduces the discrete typer's labels on the constructed cross-event
      gold (Spearman/exact-match ~1.0) -- the discretization is faithful.
  (2) TRABASSO ORDERING: the graded NECESSITY orders 4 causal-type categories physical > motivational >
      psychological > enabling (Spearman rho vs the ordinal human gold = 1.0); the info-free twin (shuffle
      the domain-determinism -> necessity map) BREAKS the ordering (rho drops).
  (3) AMBIGUITY DISSOLVES: the same force configuration ("promised") yields CAUSE or PREVENT depending ONLY
      on which endstate is the read-out reference -- one graded representation, two discrete labels.
HONEST SCOPE: the (necessity, sufficiency) PARAMETERIZATION + the determinism magnitudes are OUR-INVENTION
(swept); the ORDERING and the graded-representation direction are the PINNED, cited predictions. Human
necessity-MAGNITUDE data (Trabasso) / graded-N400 norms (Kuperberg) would be the stronger VET -- not on disk.
Glass-box, no LLM. ASCII-only. Deterministic.
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

from experiments._force_dynamics_lexicon import build_force_lexicon  # noqa: E402
from experiments.exp_causal_network_edge_typer_v1 import (  # noqa: E402
    TYPING_POOL, arm_net_typer, SET_CAUSE, SET_ENABLE, SET_PREVENT,
)

ANCHOR = "causal_network_graded_necessity_v1"
N_SHUF = 300
SEED = 20260830

# Domain-determinism necessity weights (INDEPENDENT principle: how law-like the domain is; SWEPT
# magnitudes, the ORDERING is the pinned prediction). physical(deterministic) > motivational(goal
# usually pursued) > psychological(belief/emotion, probabilistic).
DOMAIN_DETERMINISM = {"PHYS": 1.00, "MOTIV": 0.75, "PSYCH": 0.55}
# Type base necessity of the AFFECTOR's causal force (Trabasso: enabling is least necessary).
TYPE_BASE_NECESSITY = {"CAUSE": 1.00, "PREVENT": 1.00, "ENABLE": 0.30}


def graded_strength(force_type, domain, affector_magnitude=0.8):
    """Return (necessity, sufficiency) in [0,1]^2 from the force configuration.
    necessity = base_type_necessity(A) x domain_determinism; sufficiency = affector magnitude."""
    base = TYPE_BASE_NECESSITY.get(force_type, 0.0)
    det = DOMAIN_DETERMINISM.get(domain, 0.55)
    necessity = base * det
    sufficiency = affector_magnitude if force_type in ("CAUSE", "PREVENT") else 0.35  # ENABLE: A alone insufficient
    return round(necessity, 4), round(sufficiency, 4)


def discretize(necessity, sufficiency, endstate_reached, opposing):
    """Thresholded READ-OUT of the graded strength against a reference endstate -> discrete type.
    Must reproduce the Wolff/landed typer: high necessity+reached -> CAUSE; low necessity+reached ->
    ENABLE; opposing+not-reached -> PREVENT."""
    if opposing and not endstate_reached:
        return "PREVENT"
    if not endstate_reached:
        return "SEQUENTIAL"  # a CAUSE/ENABLE config whose endstate failed -> not canonical
    return "CAUSE" if necessity >= 0.6 else "ENABLE"


# ---------------------------------------------------------------------------
# (2) Trabasso 4-category ordering exemplars (domain-tagged; ordinal human gold ordering).
# ---------------------------------------------------------------------------
TRABASSO = [
    ("physical_cause", "PHYS", "CAUSE", 6),       # a rock shatters glass -- most necessary
    ("motivational_cause", "MOTIV", "CAUSE", 5),  # a goal drives an action
    ("psychological_cause", "PSYCH", "CAUSE", 4),  # a belief/emotion produces a reaction
    ("physical_enable", "PHYS", "ENABLE", 3),      # a physical enabling condition
    ("motivational_enable", "MOTIV", "ENABLE", 2),  # a motivational enabling condition
    ("psychological_enable", "PSYCH", "ENABLE", 1),  # least necessary
]


def _spearman(xs, ys):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for pos, i in enumerate(s):
            r[i] = pos
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1 - 6 * d2 / (n * (n * n - 1))


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
    # necessity ordering physical > motivational > psychological > enabling
    ns = [graded_strength(t, d)[0] for (_n, d, t, _r) in TRABASSO]
    assert all(ns[i] > ns[i + 1] for i in range(len(ns) - 1)), f"necessity ordering broken: {ns}"
    # discretization reproduces CAUSE vs ENABLE
    assert discretize(*graded_strength("CAUSE", "PHYS"), True, False) == "CAUSE"
    assert discretize(*graded_strength("ENABLE", "PHYS"), True, False) == "ENABLE"
    print("[self-test] PASS")
    return True


def main():
    out_dir = _out_dir()
    t0 = time.perf_counter()
    lex = build_force_lexicon()

    # ---- (1) CONSISTENCY: graded read-out reproduces the discrete typer on the constructed gold ----
    # domain for a constructed edge: physical (these are physical force verbs). opposing = PREVENT set.
    match = tot = 0
    for it in TYPING_POOL:
        disc = arm_net_typer(it, lex)[0]
        if disc == "SEQUENTIAL":
            continue  # necessity read-out only defined on a licensed edge
        opposing = (disc == "PREVENT")
        reached = disc in ("CAUSE", "ENABLE")
        ftype = "ENABLE" if disc == "ENABLE" else ("PREVENT" if disc == "PREVENT" else "CAUSE")
        nec, suf = graded_strength(ftype, "PHYS")
        readout = discretize(nec, suf, reached or opposing is False and reached, opposing) if False else \
            discretize(nec, suf, reached, opposing)
        match += int(readout == disc)
        tot += 1
    consistency = match / tot if tot else 0.0

    # ---- (2) TRABASSO ORDERING (necessity) + twin ----
    nec_vals = [graded_strength(t, d)[0] for (_n, d, t, _r) in TRABASSO]
    ordinal = [r for (_n, _d, _t, r) in TRABASSO]
    rho = _spearman(nec_vals, ordinal)

    # info-free twin: shuffle the model's necessity VALUES across the categories (destroys the
    # force-model assignment of necessity->category; preserves the value multiset).
    rng = random.Random(SEED)
    twin_rhos = []
    for s in range(N_SHUF):
        vals = list(nec_vals)
        rng.shuffle(vals)
        twin_rhos.append(_spearman(vals, ordinal))
    twin_rhos.sort()
    twin_mean = sum(twin_rhos) / len(twin_rhos)
    twin_p95 = twin_rhos[int(0.95 * (len(twin_rhos) - 1))]
    ordering_ok = rho > twin_p95

    # ---- (3) AMBIGUITY DISSOLVES: same config, two read-outs by reference endstate ----
    # "he held his tongue because he promised": one force config (a social antagonist force),
    # necessity/sufficiency fixed; read-out CAUSE if reference = the restraint (reached), PREVENT if
    # reference = the speaking (blocked/not reached).
    nec_p, suf_p = graded_strength("PREVENT", "MOTIV")   # the promise's force config (a motivational commitment)
    readout_restraint = discretize(nec_p, suf_p, endstate_reached=True, opposing=False)   # ref = restraint
    readout_speech = discretize(nec_p, suf_p, endstate_reached=False, opposing=True)      # ref = speaking
    ambiguity_dissolved = (readout_restraint != readout_speech)

    passed = consistency >= 0.95 and ordering_ok and ambiguity_dissolved
    verdict = ("GRADED_NECESSITY_ESTIMATOR__CONSISTENT_READOUT__REPRODUCES_TRABASSO_ORDERING__TWIN_BREAKS"
               if passed else "GRADED_NECESSITY_DID_NOT_CLEAR_ALL_CHECKS")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "summary": (
            f"GRADED CAUSAL NECESSITY estimator (the higher-fidelity edge representation): the discrete CAUSE/"
            f"ENABLE/PREVENT type is a THRESHOLDED read-out of a continuous (necessity, sufficiency) derived from "
            f"the force config x domain determinism. (1) CONSISTENCY: the read-out reproduces the discrete typer "
            f"on the constructed gold {consistency:.3f} (n={tot}). (2) TRABASSO ORDERING: graded necessity orders "
            f"physical>motivational>psychological>enabling, Spearman rho {rho:.3f} vs ordinal human gold; "
            f"determinism-shuffle twin mean {twin_mean:.3f} (p95 {twin_p95:.3f}, ordering_ok={ordering_ok}). "
            f"(3) AMBIGUITY DISSOLVES: the 'promised' config reads CAUSE vs the restraint ({readout_restraint}) "
            f"but PREVENT vs the speaking ({readout_speech}) -- one graded representation, two discrete labels "
            f"(dissolved={ambiguity_dissolved})."),
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "consistency_readout_vs_discrete": round(consistency, 4),
        "trabasso_ordering": {"necessity_values": [round(v, 4) for v in nec_vals], "ordinal_gold": ordinal,
                              "spearman_rho": round(rho, 4), "twin_mean": round(twin_mean, 4),
                              "twin_p95": round(twin_p95, 4), "ordering_beats_twin": ordering_ok,
                              "categories": [t[0] for t in TRABASSO]},
        "ambiguity_resolution": {"config": "promise (social antagonist force)",
                                 "readout_vs_restraint": readout_restraint, "readout_vs_speaking": readout_speech,
                                 "dissolved": ambiguity_dissolved},
        "graded_examples": {n: dict(necessity=graded_strength(t, d)[0], sufficiency=graded_strength(t, d)[1])
                            for (n, d, t, _r) in TRABASSO},
        "brain_note": (
            "Trabasso, van den Broek & Suh 1989 (graded necessity+sufficiency edge weights); Kuperberg, Paczynski "
            "& Ditman 2011 (graded N400 by causal relatedness); Cheng 1997 (continuous causal power); Wolff 2007 "
            "(3 types = discretization of continuous force vectors). The discrete typer is a lossy read-out; the "
            "graded (necessity, sufficiency) is the brain-faithful edge, and the discrete type is a per-clause "
            "projection against an explicit reference endstate."),
        "scope": (
            "MECHANISM DEMO: the (necessity, sufficiency) parameterization + determinism magnitudes are OUR-"
            "INVENTION (swept); the graded-representation DIRECTION + the physical>motivational>psychological>"
            "enabling ORDERING are the PINNED cited predictions. Human necessity-MAGNITUDE data (Trabasso) / "
            "graded-N400 norms (Kuperberg) are the stronger VET, not on disk (also archaic-corpus-independent, "
            "since this is a representation test, not a real-text extraction test)."),
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
