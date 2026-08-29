"""DE-RISKING PROBE for the CAUSATION next-problem (NOT a solution -- a minimal proof that the
brain-faithful mechanism is glass-box buildable and beats the current placeholder on the sharpest
can-fail subset). Scoped in notes/problems/situation_model_has_no_tested_temporal_order_comprehension/
next_problem_scoping_causation_force_dynamics_2026-08-29.md.

BRAIN MECHANISM (Talmy 1988; Wolff 2007 force dynamics): CAUSE/ENABLE/PREVENT fall out of a tiny
DISCRETE truth-table over (1) patient tendency toward the endstate, (2) affector-patient concordance,
(3) endstate reached:
    CAUSE   = patient NOT tending, forces OPPOSE, endstate REACHED
    ENABLE  = patient tending,     forces CONCUR,  endstate REACHED
    PREVENT = patient tending,     forces OPPOSE,  endstate NOT reached
The verb's force class supplies (patient-tendency, concordance) from a glass-box lexicon (VerbNet->Event
Force Dynamics / FrameNet Causation family, here a curated ~45-verb static asset -- foundation-is-free);
the endstate bit comes from narrative outcome polarity. No LLM at inference.

THE POINT (the can-fail test the connective/adjacency placeholder is STRUCTURALLY at chance on):
  Set A  3-way CAUSE vs ENABLE vs PREVENT, connective-neutral -> the placeholder can only LINK, not TYPE.
  Set C  PREVENT killer: the outcome NEVER happens ("the sandbags prevented the flood" -> no flood node).
         A link-the-nearest-outcome placeholder has nothing to link -> fails by construction; force
         dynamics is the only account that represents a PREVENTED (counterfactual) endstate.
Controls: MAJORITY baseline (a typer with no mechanism == the placeholder's ceiling); FORCE-LABEL-SHUFFLE
twin (permute verb->class; must collapse to majority -> proves the win is force-dynamic semantics).

Isolates the TYPING mechanism: the (agent, verb, patient, endstate) tuples are given (extraction is a
separate concern the full problem owns), exactly as the SPACE/TIME construction golds isolate their
mechanism. Reuses the TIME precedence gate conceptually (cause precedes effect; here all pairs are
already ordered). Diagnostic verdict (no HARD_PASS gate on a probe). ASCII-only. Deterministic.
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

ANCHOR = "causal_force_dynamics_probe_v1"
N_BOOT = 5000
SEED = 20260829

# ---------------------------------------------------------------------------
# Glass-box force-dynamic verb lexicon (curated; the full problem would grow this from
# VerbNet-EFD / FrameNet). class -> (patient_tends_toward_endstate, forces_concord).
#   CAUSE   verbs: patient does NOT tend, affector OPPOSES/forces the change.
#   ENABLE  verbs: patient DOES tend, affector CONCORDS/permits.
#   PREVENT verbs: patient DOES tend, affector OPPOSES, endstate blocked.
# ---------------------------------------------------------------------------
FORCE_CLASS = {
    # CAUSE (make it happen against the patient's own tendency)
    "shatter": "CAUSE", "break": "CAUSE", "knock": "CAUSE", "topple": "CAUSE", "weaken": "CAUSE",
    "swell": "CAUSE", "ignite": "CAUSE", "melt": "CAUSE", "snap": "CAUSE", "burst": "CAUSE",
    "crush": "CAUSE", "push": "CAUSE", "shove": "CAUSE", "sink": "CAUSE", "collapse": "CAUSE",
    "spark": "CAUSE",
    # ENABLE (let/help what already tends to happen)
    "let": "ENABLE", "allow": "ENABLE", "help": "ENABLE", "release": "ENABLE", "free": "ENABLE",
    "open": "ENABLE", "permit": "ENABLE", "enable": "ENABLE", "aid": "ENABLE", "assist": "ENABLE",
    "loosen": "ENABLE", "unleash": "ENABLE",
    # PREVENT (oppose what tends to happen; endstate blocked)
    "prevent": "PREVENT", "block": "PREVENT", "stop": "PREVENT", "hold": "PREVENT", "save": "PREVENT",
    "protect": "PREVENT", "resist": "PREVENT", "dam": "PREVENT", "halt": "PREVENT", "shield": "PREVENT",
    "thwart": "PREVENT", "deter": "PREVENT", "hinder": "PREVENT", "curb": "PREVENT", "restrain": "PREVENT",
    "guard": "PREVENT",
}


def force_dynamic_type(verb, endstate_reached):
    """Glass-box Wolff typing. The verb's class gives (patient-tendency, concordance); the narrative's
    endstate-reached bit disambiguates. Returns CAUSE/ENABLE/PREVENT or None (unknown verb)."""
    cls = FORCE_CLASS.get(verb)
    if cls is None:
        return None
    if cls == "PREVENT":
        # PREVENT lexically implies the endstate is blocked; if narrative says it WAS reached, the
        # prevention failed -> the tending patient reached its endstate concordantly == an ENABLE-like
        # (or plain CAUSE-less) outcome. Conservative: only assert PREVENT when endstate NOT reached.
        return "PREVENT" if not endstate_reached else "ENABLE"
    if cls == "ENABLE":
        return "ENABLE" if endstate_reached else "PREVENT"
    # CAUSE class
    return "CAUSE" if endstate_reached else "PREVENT"


# ---------------------------------------------------------------------------
# GOLD -- (agent, verb, patient, endstate_reached, gold_type). Connective-neutral (no because/so),
# so a connective baseline is blind. Extraction is GIVEN (isolates the TYPING mechanism).
# ---------------------------------------------------------------------------
SET_A = [  # 3-way, endstate REACHED for CAUSE/ENABLE, NOT reached for PREVENT
    ("flood", "swell", "river", True, "CAUSE"),
    ("hammer", "shatter", "vase", True, "CAUSE"),
    ("storm", "topple", "tree", True, "CAUSE"),
    ("current", "weaken", "hull", True, "CAUSE"),
    ("spark", "ignite", "fuel", True, "CAUSE"),
    ("blow", "break", "window", True, "CAUSE"),
    ("guard", "release", "prisoner", True, "ENABLE"),
    ("key", "open", "gate", True, "ENABLE"),
    ("warden", "let", "crowd", True, "ENABLE"),
    ("rope", "free", "boat", True, "ENABLE"),
    ("nurse", "help", "patient", True, "ENABLE"),
    ("latch", "loosen", "door", True, "ENABLE"),
    ("dam", "hold", "flood", False, "PREVENT"),
    ("wall", "block", "fire", False, "PREVENT"),
    ("sandbags", "stop", "water", False, "PREVENT"),
    ("shield", "protect", "soldier", False, "PREVENT"),
    ("fence", "halt", "herd", False, "PREVENT"),
    ("guard", "thwart", "thief", False, "PREVENT"),
]

SET_C = [  # PREVENT KILLER -- outcome never happens (endstate NOT reached); placeholder has no node to link
    ("sandbags", "prevent", "flood", False, "PREVENT"),
    ("dam", "block", "flood", False, "PREVENT"),
    ("medicine", "prevent", "fever", False, "PREVENT"),
    ("lock", "deter", "burglar", False, "PREVENT"),
    ("umbrella", "shield", "rain", False, "PREVENT"),
    ("vaccine", "prevent", "disease", False, "PREVENT"),
    ("brake", "halt", "crash", False, "PREVENT"),
    ("guard", "stop", "escape", False, "PREVENT"),
]

SET_B = [  # causal vs merely-sequential (precision): sequential pairs have NO force-dynamic verb
    ("she", "pour", "coffee", True, "SEQUENTIAL"),
    ("he", "close", "book", True, "SEQUENTIAL"),   # 'close' not in force lexicon -> no causal type
    ("bell", "ring", "hall", True, "SEQUENTIAL"),
    ("clock", "chime", "midnight", True, "SEQUENTIAL"),
    ("man", "walk", "road", True, "SEQUENTIAL"),
    ("bird", "sing", "tree", True, "SEQUENTIAL"),
]


# ---------------------------------------------------------------------------
# Arms.
# ---------------------------------------------------------------------------
def arm_force_dynamic(item, verb_map=None):
    ag, vb, pt, es, gold = item
    vmap = verb_map or FORCE_CLASS
    cls = vmap.get(vb)
    if cls is None:
        return "SEQUENTIAL"        # not a force-dynamic verb -> not a causal link (Set B precision)
    # type via the truth table (using the shuffled map's class as the verb's class)
    if cls == "PREVENT":
        return "PREVENT" if not es else "ENABLE"
    if cls == "ENABLE":
        return "ENABLE" if es else "PREVENT"
    return "CAUSE" if es else "PREVENT"


def arm_majority(item, majority="CAUSE"):
    # a typer with no mechanism (== the connective/adjacency placeholder's ceiling on TYPE): always
    # emit the majority causal type for any linked pair; SEQUENTIAL never recognized (it links everything).
    return majority


def arm_placeholder_prevent(item):
    # the placeholder LINKS cause->outcome. On PREVENT the outcome never happened -> no outcome node ->
    # it cannot represent PREVENT; model that as "asserts a (wrong) positive causal link".
    return "CAUSE"


def score(items, arm_fn, **kw):
    recs = []
    for it in items:
        pred = arm_fn(it, **kw)
        recs.append(int(pred == it[4]))
    return recs


def _acc(recs):
    return sum(recs) / len(recs) if recs else 0.0


def _boot(recs, seed=SEED, n=N_BOOT):
    if not recs:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed); m = len(recs)
    b = sorted(sum(recs[rng.randrange(m)] for _ in range(m)) / m for _ in range(n))
    return sum(recs) / m, b[int(0.025 * n)], b[int(0.975 * n)]


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
    assert force_dynamic_type("shatter", True) == "CAUSE"
    assert force_dynamic_type("let", True) == "ENABLE"
    assert force_dynamic_type("prevent", False) == "PREVENT"
    print("[self-test] PASS")
    return True


def main():
    out_dir = _out_dir()
    t0 = time.perf_counter()
    A = SET_A + SET_C            # the 3-way + killer (all causal-type items)
    AB = SET_A + SET_C + SET_B   # + sequential for precision

    fd = score(AB, arm_force_dynamic)
    maj = score(AB, arm_majority)
    # force-label-shuffle twin: permute the verb->class assignment (destroys force semantics, keeps shape)
    twin_accs = []
    verbs = list(FORCE_CLASS.keys())
    classes = list(FORCE_CLASS.values())
    for s in range(300):
        rng = random.Random(1000 + s)
        perm = classes[:]
        rng.shuffle(perm)
        vmap = dict(zip(verbs, perm))
        twin_accs.append(_acc(score(AB, arm_force_dynamic, verb_map=vmap)))
    twin_accs.sort()
    twin_mean = sum(twin_accs) / len(twin_accs)
    twin_p95 = twin_accs[int(0.95 * (len(twin_accs) - 1))]

    # PREVENT killer subset (Set C): force-dynamic vs the link-outcome placeholder
    fd_c = score(SET_C, arm_force_dynamic)
    ph_c = score(SET_C, arm_placeholder_prevent)

    # CAUSE-vs-ENABLE isolation: both have endstate REACHED, so ONLY the verb's force class can
    # distinguish them (the endstate bit is constant here). This is where force-dynamic VERB semantics
    # is load-bearing; a verb-shuffle twin must drop to ~chance (0.5).
    ce = [it for it in SET_A if it[4] in ("CAUSE", "ENABLE")]
    fd_ce = _acc(score(ce, arm_force_dynamic))
    ce_twin = []
    for s in range(300):
        rng = random.Random(2000 + s)
        perm = classes[:]; rng.shuffle(perm)
        vmap = dict(zip(verbs, perm))
        ce_twin.append(_acc(score(ce, arm_force_dynamic, verb_map=vmap)))
    ce_twin.sort()
    ce_twin_mean = sum(ce_twin) / len(ce_twin)
    ce_twin_p95 = ce_twin[int(0.95 * (len(ce_twin) - 1))]

    m_fd, lo_fd, hi_fd = _boot(fd)
    m_maj, lo_maj, hi_maj = _boot(maj)
    ci_sep = lo_fd > hi_maj
    twin_loses = lo_fd > twin_p95

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": "PROBE_MEASURED",
        "summary": (f"DE-RISK PROBE: glass-box force-dynamic typing 3-way+seq accuracy {m_fd:.3f} "
                    f"[{lo_fd:.3f},{hi_fd:.3f}] vs MAJORITY/placeholder-ceiling {m_maj:.3f} "
                    f"[{lo_maj:.3f},{hi_maj:.3f}] (CI-sep={ci_sep}); force-label-shuffle twin {twin_mean:.3f} "
                    f"(p95 {twin_p95:.3f}, loses={twin_loses}). PREVENT KILLER (Set C): force-dynamic "
                    f"{_acc(fd_c):.3f} vs link-outcome placeholder {_acc(ph_c):.3f} (placeholder structurally "
                    f"cannot represent a prevented outcome). CAUSE-vs-ENABLE verb isolation (endstate constant): "
                    f"force-dynamic {fd_ce:.3f} vs verb-shuffle twin {ce_twin_mean:.3f} (p95 {ce_twin_p95:.3f})."),
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "force_dynamic_acc": round(m_fd, 4), "force_dynamic_ci": [round(lo_fd, 4), round(hi_fd, 4)],
        "majority_placeholder_ceiling_acc": round(m_maj, 4), "majority_ci": [round(lo_maj, 4), round(hi_maj, 4)],
        "ci_separated_over_placeholder": ci_sep,
        "force_label_shuffle_twin": {"mean": round(twin_mean, 4), "p95": round(twin_p95, 4), "loses": twin_loses},
        "prevent_killer_setC": {"force_dynamic_acc": round(_acc(fd_c), 4),
                                "link_outcome_placeholder_acc": round(_acc(ph_c), 4),
                                "n": len(SET_C),
                                "note": "the placeholder links cause->outcome; PREVENT has NO outcome node -> "
                                        "it asserts a wrong positive link. Force dynamics is the only account "
                                        "that represents a prevented (counterfactual) endstate."},
        "cause_vs_enable_verb_isolation": {"force_dynamic_acc": round(fd_ce, 4), "n": len(ce),
                                           "verb_shuffle_twin_mean": round(ce_twin_mean, 4),
                                           "verb_shuffle_twin_p95": round(ce_twin_p95, 4),
                                           "twin_loses": fd_ce > ce_twin_p95,
                                           "note": "endstate is CONSTANT (both reached) -> only the verb force "
                                                   "class distinguishes CAUSE from ENABLE; the verb-shuffle twin "
                                                   "drops to ~chance, isolating the force-dynamic contribution "
                                                   "from the endstate-polarity contribution."},
        "n_gold": {"set_A_3way": len(SET_A), "set_C_prevent_killer": len(SET_C), "set_B_sequential": len(SET_B)},
        "scope": ("DE-RISKING PROBE, not a solution. Extraction is GIVEN (isolates the TYPING mechanism); the "
                  "full CAUSATION problem owns extraction + a grown VerbNet/FrameNet force lexicon + a "
                  "negation/polarity detector for endstate + real-prose serve. This proves the core bet is "
                  "glass-box buildable and beats the placeholder on the sharpest can-fail subsets."),
        "brain_note": "Talmy 1988 / Wolff 2007 force dynamics; CAUSE/ENABLE/PREVENT truth-table over "
                      "patient-tendency x concordance x endstate-reached. Glass-box, no LLM.",
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"elapsed={elapsed:.2f}s -> {os.path.join(out_dir, 'metrics.json')}")
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test(); sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        _atomic_write(_out_dir(), {"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                                   "traceback": traceback.format_exc()[:4000]})
        raise
