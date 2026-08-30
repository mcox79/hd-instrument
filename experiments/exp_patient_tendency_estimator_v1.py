"""THE FULL PATIENT-TENDENCY ESTIMATOR for the Wolff force-dynamic CAUSE/ENABLE typer.
   problem: causation_typing_needs_a_patient_tendency_estimator

The landed Wolff typer reads CAUSE/ENABLE from the verb's force class, which is CAPPED AT 0.500 on
tendency-ambiguous verbs (open/move/turn/roll/...): patient-tendency is not in the verb. The prior
integration PROVED one recovering term (affector MAGNITUDE, exp_causal_tendency_recovery_v1: 0.500 ->
1.000 on magnitude-cued pairs, twin at chance, held-out generalization). This cell builds and validates
the FULL estimator = a signed PATIENT-SIDE force sum of three Wolff force terms:
  (1) affector-MAGNITUDE  -- PROVEN abductive term (weak affector + reached => patient tended).
  (2) patient-AFFORDANCE  -- core-physics disposition (round/buoyant/hinged tends; heavy/anchored resists).
  (3) DIRECTIONAL/GRAVITY -- environmental force ("down the slope"/"with the current" aligns).
sign(sum) => concordance with the affector (which points to the reached endstate) => ENABLE (tends) /
CAUSE (resists). Force-sum + concordance read-out is PINNED to Wolff 2007 (JEP:General 136) / Wolff &
Barbey 2015 (Front.Hum.Neurosci. 9:1); see _patient_tendency.py.

WHY THE FULL ESTIMATOR BEATS THE PROVEN FIRST TERM: the affector-magnitude term FALLS BACK to the verb
(0.500) whenever the affector magnitude is unstated/neutral. The affordance + directional terms type
those magnitude-silent cases. So the payoff is measured on cue-ISOLATED populations where each term is
the SOLE discriminator (the other two cues are 0), plus a combined population and held-out sets.

CONTROLS (each excludes something):
  * lexicon-only floor (0.500 cap, recomputed on-population) -- excludes "the verb already does it".
  * affector-MAGNITUDE-ALONE floor (the proven first term) -- the sharp floor: the full estimator must
    beat the proven term CI-separated on the magnitude-silent population, else the added terms are
    redundant (a rigorous NEGATIVE the brief invites).
  * info-free TWIN: permute each cue's contribution across items (same +1/-1/0 shape, no correlation to
    gold) -> must fall to chance. Excludes "any three-signal blend would score".
  * per-term ABLATION + leave-one-out -> which term carries the signal (the mechanism decomposition).
  * HELD-OUT affectors / patients / directional cues -> generalization, not fit to the construction set.
  * WEIGHT SWEEP -> robust to the OUR-INVENTION combination weights (not fitted).
  * POSITIVE CONTROL minimal pairs (incl. the brief's key-vs-wind) the estimator gets & lexicon cannot.

HONEST SCOPE: constructed minimal pairs with (affector, verb, patient, context) GIVEN (as the proven
demo and the base typer's own eval were). The affordance property->sign lexicon is OUR-INVENTION-
UNDER-TEST (Wolff PINS the patient-force source; the specific map is ours) -- gated on the twin +
held-out + positive control, not face validity. Real-text auto-extraction is the named follow-on.
ASCII-only. Deterministic. No torch, no LLM.
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

from experiments._force_dynamics_lexicon import build_force_lexicon, force_dynamic_type  # noqa: E402
from experiments._patient_tendency import (  # noqa: E402
    affector_magnitude_sign, patient_affordance_sign, directional_sign, affector_letting_sign,
    type_with_full_tendency, AMBIGUOUS_VERBS,
)
# cross-check that we reuse the PROVEN first term faithfully (not re-derived)
from experiments.exp_causal_tendency_recovery_v1 import type_with_tendency as demo_magnitude_only  # noqa: E402

ANCHOR = "patient_tendency_estimator_v1"
SEED = 20260830
N_BOOT = 2000
N_TWIN = 400
N_NULL = 2000

# ---------------------------------------------------------------------------
# POPULATIONS. Each item = (affector, verb, patient, context_tokens, gold in {CAUSE,ENABLE}).
# Endstate REACHED in all (CAUSE and ENABLE both reach it; the discriminator is patient tendency).
# Each cue-ISOLATED set is neutral on the other two cues (asserted in self_test).
# ---------------------------------------------------------------------------
NEUTRAL_AFF = "machine"          # magnitude sign 0
NEUTRAL_PAT = "keg"              # affordance sign 0 for the ambiguous verbs

# --- Set M: MAGNITUDE-isolated (neutral patient, no directional). Weak->ENABLE, strong->CAUSE. ---
SET_M = [
    ("nudge", "move", NEUTRAL_PAT, [], "ENABLE"),   ("shove", "move", NEUTRAL_PAT, [], "CAUSE"),
    ("breeze", "turn", NEUTRAL_PAT, [], "ENABLE"),  ("winch", "turn", NEUTRAL_PAT, [], "CAUSE"),
    ("tap", "roll", NEUTRAL_PAT, [], "ENABLE"),     ("heave", "roll", NEUTRAL_PAT, [], "CAUSE"),
    ("touch", "slide", NEUTRAL_PAT, [], "ENABLE"),  ("wrench", "slide", NEUTRAL_PAT, [], "CAUSE"),
    ("tide", "raise", NEUTRAL_PAT, [], "ENABLE"),   ("crane", "raise", NEUTRAL_PAT, [], "CAUSE"),
    ("updraft", "lift", NEUTRAL_PAT, [], "ENABLE"), ("jack", "lift", NEUTRAL_PAT, [], "CAUSE"),
    ("current", "drive", NEUTRAL_PAT, [], "ENABLE"),("piston", "drive", NEUTRAL_PAT, [], "CAUSE"),
]
# --- Set A: AFFORDANCE-isolated (neutral affector, no directional). Labile->ENABLE, inert->CAUSE. ---
SET_A = [
    (NEUTRAL_AFF, "move", "ball", [], "ENABLE"),    (NEUTRAL_AFF, "move", "crate", [], "CAUSE"),
    (NEUTRAL_AFF, "roll", "barrel", [], "ENABLE"),  (NEUTRAL_AFF, "roll", "vault", [], "CAUSE"),
    (NEUTRAL_AFF, "raise", "boat", [], "ENABLE"),   (NEUTRAL_AFF, "raise", "hull", [], "CAUSE"),
    (NEUTRAL_AFF, "lift", "balloon", [], "ENABLE"), (NEUTRAL_AFF, "lift", "anvil", [], "CAUSE"),
    (NEUTRAL_AFF, "swing", "door", [], "ENABLE"),   (NEUTRAL_AFF, "swing", "pillar", [], "CAUSE"),
    (NEUTRAL_AFF, "turn", "vane", [], "ENABLE"),    (NEUTRAL_AFF, "turn", "column", [], "CAUSE"),
    (NEUTRAL_AFF, "slide", "drawer", [], "ENABLE"), (NEUTRAL_AFF, "slide", "safe", [], "CAUSE"),
]
# --- Set D: DIRECTIONAL-isolated (neutral affector + neutral patient). down/with->ENABLE, up/against->CAUSE. ---
SET_D = [
    ("force", "roll", "keg", ["down", "the", "slope"], "ENABLE"),
    ("force", "roll", "keg", ["up", "the", "slope"], "CAUSE"),
    ("force", "move", "parcel", ["downhill"], "ENABLE"),
    ("force", "move", "parcel", ["uphill"], "CAUSE"),
    ("force", "drive", "bundle", ["with", "the", "current"], "ENABLE"),
    ("force", "drive", "bundle", ["against", "the", "current"], "CAUSE"),
    ("force", "slide", "urn", ["down", "the", "chute"], "ENABLE"),
    ("force", "slide", "urn", ["up", "the", "chute"], "CAUSE"),
    ("force", "turn", "bin", ["freely"], "ENABLE"),
    ("force", "turn", "bin", ["stubbornly"], "CAUSE"),
    ("force", "drop", "case", ["on", "its", "own"], "ENABLE"),
    ("force", "drop", "case", ["jammed"], "CAUSE"),
]

# --- HELD-OUT sets (fresh affectors / patients / cues NOT used to design the estimator) ---
HELDOUT_M = [  # fresh magnitude affectors (in the general lexicon, not in SET_M)
    ("gust", "push", NEUTRAL_PAT, [], "ENABLE"),   ("bulldozer", "push", NEUTRAL_PAT, [], "CAUSE"),
    ("ripple", "rock", NEUTRAL_PAT, [], "ENABLE"), ("sledgehammer", "rock", NEUTRAL_PAT, [], "CAUSE"),
    ("draft", "swing", NEUTRAL_PAT, [], "ENABLE"), ("ram", "swing", NEUTRAL_PAT, [], "CAUSE"),
]
HELDOUT_A = [  # fresh patients (same core-physics properties, absent from SET_A)
    (NEUTRAL_AFF, "roll", "wheel", [], "ENABLE"),  (NEUTRAL_AFF, "roll", "chest", [], "CAUSE"),
    (NEUTRAL_AFF, "move", "cart", [], "ENABLE"),   (NEUTRAL_AFF, "move", "block", [], "CAUSE"),
    (NEUTRAL_AFF, "lift", "raft", [], "ENABLE"),   (NEUTRAL_AFF, "lift", "girder", [], "CAUSE"),
    (NEUTRAL_AFF, "swing", "flap", [], "ENABLE"),  (NEUTRAL_AFF, "swing", "post", [], "CAUSE"),
    (NEUTRAL_AFF, "move", "leaf", [], "ENABLE"),   (NEUTRAL_AFF, "move", "boulder", [], "CAUSE"),
]
HELDOUT_D = [  # fresh directional cues
    ("force", "move", "keg", ["downstream"], "ENABLE"), ("force", "move", "keg", ["upstream"], "CAUSE"),
    ("force", "roll", "parcel", ["downward"], "ENABLE"), ("force", "roll", "parcel", ["upward"], "CAUSE"),
    ("force", "drift", "bundle", ["with", "the", "wind"], "ENABLE"),
    ("force", "drift", "bundle", ["against", "the", "wind"], "CAUSE"),
]

# --- POSITIVE-CONTROL minimal pairs (the estimator gets; the verb lexicon cannot) ---
POS_CONTROL = {
    "affordance_ball_vs_crate": [
        (NEUTRAL_AFF, "move", "ball", [], "ENABLE"), (NEUTRAL_AFF, "move", "crate", [], "CAUSE")],
    "directional_down_vs_up": [
        ("force", "roll", "keg", ["down", "the", "slope"], "ENABLE"),
        ("force", "roll", "keg", ["up", "the", "slope"], "CAUSE")],
    "magnitude_nudge_vs_shove": [
        ("nudge", "move", NEUTRAL_PAT, [], "ENABLE"), ("shove", "move", NEUTRAL_PAT, [], "CAUSE")],
    # the brief's NAMED pair -- reported honestly. BARE "the wind opened the gate" is under-determined
    # (partly linguistically CONSTRUED, Kuhnmuench & Beller 2005): a breeze nudging an ajar gate = ENABLE,
    # a gale forcing a shut gate = CAUSE. With rest-state honesty the gate does not afford "open", so both
    # fall to the verb lexicon (the estimator correctly declines to invent tendency it cannot read).
    "brief_key_vs_wind_bare": [
        ("key", "open", "gate", [], "ENABLE"), ("wind", "open", "gate", [], "CAUSE")],
    # ... but once the construed force MAGNITUDE is stated, the estimator resolves the flagship case:
    "gate_breeze_vs_blast": [
        ("breeze", "open", "gate", [], "ENABLE"), ("blast", "open", "gate", [], "CAUSE")],
}

# --- Set L: CAUSING-vs-LETTING (the 4th cue, Talmy 1988). ENABLE = a restraint-remover instrument
# (key/latch/catch/valve/floodgate/clasp) LETS the result -> letting; CAUSE = a strong force-applier
# (winch/ram/jack/...) OVERCOMES -> causing. Patients are hinged (gate/door/lid/hatch): with rest-state
# honesty they do NOT afford "open" (a=0), so ONLY the affector role separates the two. The verb "open"
# is ambiguous -> decided by the affector-instrument class, exactly the drill's design guidance. ---
SET_L = [
    ("key", "open", "gate", [], "ENABLE"),       ("winch", "open", "gate", [], "CAUSE"),
    ("latch", "open", "door", [], "ENABLE"),     ("ram", "open", "door", [], "CAUSE"),
    ("catch", "open", "lid", [], "ENABLE"),      ("jack", "open", "lid", [], "CAUSE"),
    ("valve", "open", "hatch", [], "ENABLE"),    ("hydraulic", "open", "hatch", [], "CAUSE"),
    ("floodgate", "open", "gate", [], "ENABLE"), ("crane", "open", "door", [], "CAUSE"),
    ("clasp", "open", "lid", [], "ENABLE"),      ("piston", "open", "hatch", [], "CAUSE"),
]
# HELD-OUT letting cues: fresh restraint-removal via CONTEXT (the "un-" family) + fresh instruments.
HELDOUT_L = [
    ("hand", "open", "gate", ["unlocked"], "ENABLE"),   ("hand", "open", "gate", ["forced"], "CAUSE"),
    ("cork", "open", "hatch", [], "ENABLE"),            ("bulldozer", "open", "hatch", [], "CAUSE"),
    ("worker", "open", "door", ["unbarred"], "ENABLE"), ("worker", "open", "door", ["smashed"], "CAUSE"),
]
# NEGATIVE control: ONSET-CAUSE instruments (switch/trigger/lever) APPLY AN IMPULSE -> causing, NOT
# letting; they must NEVER be typed ENABLE by the letting cue (they fall to the verb lexicon).
ONSET_CAUSE_NEGCTRL = [
    ("switch", "open", "gate", []), ("trigger", "open", "door", []), ("lever", "open", "hatch", []),
    ("button", "open", "lid", []),
]

COMBINED = SET_M + SET_A + SET_D
HELDOUT = HELDOUT_M + HELDOUT_A + HELDOUT_D

# --- CONFLICT set: the COMBINATION-RULE discriminator. Each item has all THREE cues present with a 2-vs-1
# disagreement, and the MINORITY cue ROTATES evenly across the set (4 magnitude-minority, 4 affordance-
# minority, 4 directional-minority). gold = the NET force sign (Wolff's resultant of 3 equal-weight force
# contributions -- the majority direction). Therefore NO single-cue-priority rule can score above 8/12
# (each fails exactly the 4 items where its cue is the minority); only the ADDITIVE force-sum (Wolff vector
# addition) gets all 12. This proves the combination rule is additive integration, not winner-take-all. ---
CONFLICT = [
    # magnitude is the minority (affordance + directional agree)
    ("shove", "roll", "ball", ["down", "the", "slope"], "ENABLE"),
    ("nudge", "move", "crate", ["uphill"], "CAUSE"),
    ("winch", "slide", "drawer", ["downhill"], "ENABLE"),
    ("tap", "roll", "vault", ["up", "the", "slope"], "CAUSE"),
    # affordance is the minority (magnitude + directional agree)
    ("nudge", "roll", "vault", ["downhill"], "ENABLE"),
    ("winch", "roll", "ball", ["up", "the", "slope"], "CAUSE"),
    ("breeze", "move", "block", ["downstream"], "ENABLE"),
    ("crane", "move", "cart", ["upstream"], "CAUSE"),
    # directional is the minority (magnitude + affordance agree)
    ("nudge", "roll", "ball", ["up", "the", "slope"], "ENABLE"),
    ("winch", "move", "crate", ["downhill"], "CAUSE"),
    ("breeze", "slide", "drawer", ["upstream"], "ENABLE"),
    ("heave", "move", "block", ["downstream"], "CAUSE"),
]


# ---------------------------------------------------------------------------
# scoring helpers
# ---------------------------------------------------------------------------
def contributions(item):
    """(m,a,d,e) signed contributions for an item (endstate reached): affector-magnitude, patient-
    affordance, directional/gravity, affector-letting-role (Talmy causing-vs-letting)."""
    aff, verb, pat, ctx, _ = item
    m = affector_magnitude_sign(aff)
    a = patient_affordance_sign(pat, verb, context=ctx)
    d = directional_sign(ctx, verb)
    e = affector_letting_sign(aff, verb, ctx)
    return m, a, d, e


def type_from_contrib(m, a, d, e, verb, lexicon, w):
    T = w["m"] * m + w["a"] * a + w["d"] * d + w.get("e", 1.0) * e
    if verb in AMBIGUOUS_VERBS:
        if T > 1e-9:
            return "ENABLE"
        if T < -1e-9:
            return "CAUSE"
    return force_dynamic_type(verb, True, lexicon)


def acc_full(items, lexicon, w):
    c = 0
    for it in items:
        m, a, d, e = contributions(it)
        c += int(type_from_contrib(m, a, d, e, it[1], lexicon, w) == it[4])
    return c / len(items)


def acc_lexicon_only(items, lexicon):
    return sum(int(force_dynamic_type(it[1], True, lexicon) == it[4]) for it in items) / len(items)


def acc_magnitude_only(items, lexicon):
    """The PROVEN first term (affector magnitude alone), via the landed demo function -- the sharp floor."""
    return sum(int(demo_magnitude_only(it[0], it[1], True, lexicon) == it[4]) for it in items) / len(items)


def acc_wta(items, lexicon, cue):
    """Single-cue-priority (winner-take-all) foil: type from ONE cue's sign only; if that cue is 0, fall
    back to the verb lexicon. The non-additive alternative the force-sum must beat on CONFLICT."""
    idx = {"m": 0, "a": 1, "d": 2, "e": 3}[cue]
    c = 0
    for it in items:
        contrib = contributions(it)
        s = contrib[idx]
        if it[1] in AMBIGUOUS_VERBS and s != 0:
            pred = "ENABLE" if s > 0 else "CAUSE"
        else:
            pred = force_dynamic_type(it[1], True, lexicon)
        c += int(pred == it[4])
    return c / len(items)


def acc_majority(items):
    from collections import Counter
    maj = Counter(it[4] for it in items).most_common(1)[0][0]
    return sum(int(maj == it[4]) for it in items) / len(items)


def boot_ci(items, scorefn, n=N_BOOT, seed=SEED):
    rng = random.Random(seed)
    N = len(items)
    xs = []
    for _ in range(n):
        samp = [items[rng.randrange(N)] for _ in range(N)]
        xs.append(scorefn(samp))
    xs.sort()
    lo = xs[int(0.025 * (n - 1))]
    hi = xs[int(0.975 * (n - 1))]
    mean = sum(xs) / n
    return mean, lo, hi, (hi - lo) / 2.0


def paired_delta_ci(items, fn_hi, fn_lo, n=N_BOOT, seed=SEED):
    """Bootstrap CI of the PAIRED difference fn_hi - fn_lo over resampled items."""
    rng = random.Random(seed)
    N = len(items)
    ds = []
    for _ in range(n):
        samp = [items[rng.randrange(N)] for _ in range(N)]
        ds.append(fn_hi(samp) - fn_lo(samp))
    ds.sort()
    lo = ds[int(0.025 * (n - 1))]
    hi = ds[int(0.975 * (n - 1))]
    mean = sum(ds) / n
    band = "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": round(mean, 4), "ci": [round(lo, 4), round(hi, 4)],
            "half_width": round((hi - lo) / 2.0, 4), "band": band}


def twin_stats(items, lexicon, w, n=N_TWIN, seed=SEED):
    """Info-free twin: permute each cue contribution ACROSS items (same +1/-1/0 shape, correlation to
    gold destroyed). Must fall to chance. Returns (mean, p95)."""
    base = [contributions(it) for it in items]
    ms = [c[0] for c in base]; as_ = [c[1] for c in base]; ds = [c[2] for c in base]; es = [c[3] for c in base]
    rng = random.Random(seed)
    accs = []
    for _ in range(n):
        pm = ms[:]; pa = as_[:]; pd = ds[:]; pe = es[:]
        rng.shuffle(pm); rng.shuffle(pa); rng.shuffle(pd); rng.shuffle(pe)
        c = 0
        for i, it in enumerate(items):
            c += int(type_from_contrib(pm[i], pa[i], pd[i], pe[i], it[1], lexicon, w) == it[4])
        accs.append(c / len(items))
    accs.sort()
    return sum(accs) / n, accs[int(0.95 * (n - 1))]


def null_p95(items, scorefn, n=N_NULL, seed=SEED):
    """Label-permutation null: shuffle gold labels, rescore. p95 of the null accuracy distribution."""
    rng = random.Random(seed + 7)
    golds = [it[4] for it in items]
    accs = []
    for _ in range(n):
        pg = golds[:]; rng.shuffle(pg)
        perm = [(it[0], it[1], it[2], it[3], pg[i]) for i, it in enumerate(items)]
        accs.append(scorefn(perm))
    accs.sort()
    return accs[int(0.95 * (n - 1))]


def ablation(items, lexicon):
    """Per-term and leave-one-out accuracies (mechanism decomposition)."""
    configs = {
        "full_m+a+d+e": {"m": 1, "a": 1, "d": 1, "e": 1},
        "m_only": {"m": 1, "a": 0, "d": 0, "e": 0},
        "a_only": {"m": 0, "a": 1, "d": 0, "e": 0},
        "d_only": {"m": 0, "a": 0, "d": 1, "e": 0},
        "e_only": {"m": 0, "a": 0, "d": 0, "e": 1},
        "drop_m": {"m": 0, "a": 1, "d": 1, "e": 1},
        "drop_a": {"m": 1, "a": 0, "d": 1, "e": 1},
        "drop_d": {"m": 1, "a": 1, "d": 0, "e": 1},
        "drop_e": {"m": 1, "a": 1, "d": 1, "e": 0},
    }
    return {k: round(acc_full(items, lexicon, w), 4) for k, w in configs.items()}


def weight_sweep(items, lexicon):
    """Full estimator accuracy over a grid of weights -> robust (not fitted)."""
    grid = [0.5, 1.0, 2.0]
    accs = []
    for wm in grid:
        for wa in grid:
            for wd in grid:
                accs.append(acc_full(items, lexicon, {"m": wm, "a": wa, "d": wd}))
    return {"min": round(min(accs), 4), "max": round(max(accs), 4),
            "mean": round(sum(accs) / len(accs), 4), "n_configs": len(accs)}


# ---------------------------------------------------------------------------
def self_test():
    lex = build_force_lexicon()
    # 1. cue ISOLATION: each isolated set is neutral on the OTHER THREE cues (incl. the letting term e).
    for it in SET_M:
        m, a, d, e = contributions(it)
        assert a == 0 and d == 0 and e == 0, f"SET_M not magnitude-isolated: {it} -> a={a} d={d} e={e}"
        assert m != 0, f"SET_M item has no magnitude cue: {it}"
    for it in SET_A:
        m, a, d, e = contributions(it)
        assert m == 0 and d == 0 and e == 0, f"SET_A not affordance-isolated: {it} -> m={m} d={d} e={e}"
        assert a != 0, f"SET_A item has no affordance cue: {it}"
    for it in SET_D:
        m, a, d, e = contributions(it)
        assert m == 0 and a == 0 and e == 0, f"SET_D not directional-isolated: {it} -> m={m} a={a} e={e}"
        assert d != 0, f"SET_D item has no directional cue: {it}"
    # 1b. SET_L is a CAUSING-vs-LETTING population: ENABLE items fire the letting cue (e>0, m/a/d=0);
    #     CAUSE items fire causing-by-force (m<0), NOT letting (e=0). The affordance is neutral (a=0).
    for it in SET_L:
        m, a, d, e = contributions(it)
        assert a == 0 and d == 0, f"SET_L not affector-role-isolated (a/d must be 0): {it}"
        if it[4] == "ENABLE":
            assert e > 0 and m == 0, f"SET_L ENABLE item must be letting-only: {it} -> m={m} e={e}"
        else:
            assert m < 0 and e == 0, f"SET_L CAUSE item must be causing-by-force: {it} -> m={m} e={e}"
    # 1c. dropping the letting cue collapses the ENABLE (letting) side -> the cue carries it.
    assert acc_full(SET_L, lex, {"m": 1, "a": 1, "d": 1, "e": 1}) == 1.0, "full != 1.0 on SET_L"
    assert acc_full(SET_L, lex, {"m": 1, "a": 1, "d": 1, "e": 0}) < 0.7, "drop_e should collapse SET_L ENABLEs"
    # 1d. ONSET-CAUSE instruments (switch/trigger/lever) are NOT typed ENABLE (the disambiguation guard).
    for (aff, v, p, ctx) in ONSET_CAUSE_NEGCTRL:
        assert type_with_full_tendency(aff, v, p, ctx, True, lex) != "ENABLE", \
            f"onset-cause instrument wrongly typed ENABLE: {aff} {v} {p}"
    # 2. the m-only ablation reproduces the PROVEN demo function exactly (faithful reuse).
    for it in SET_M + HELDOUT_M:
        m, a, d, e = contributions(it)
        mine = type_from_contrib(m, 0, 0, 0, it[1], lex, {"m": 1, "a": 0, "d": 0, "e": 0})
        theirs = demo_magnitude_only(it[0], it[1], True, lex)
        assert mine == theirs, f"m-only != demo on {it}: {mine} vs {theirs}"
    # 3. lexicon-only is exactly the 0.500 cap on each isolated set.
    for name, s in [("M", SET_M), ("A", SET_A), ("D", SET_D)]:
        assert abs(acc_lexicon_only(s, lex) - 0.5) < 1e-9, f"lexicon-only != 0.5 on SET_{name}"
    # 4. full estimator perfect on each isolated set.
    for name, s in [("M", SET_M), ("A", SET_A), ("D", SET_D)]:
        assert acc_full(s, lex, {"m": 1, "a": 1, "d": 1}) == 1.0, f"full != 1.0 on SET_{name}"
    print("[self-test] PASS (cue isolation, faithful reuse of proven term, 0.5 cap, full=1.0)")
    return True


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _pop_block(name, items, lex):
    w = {"m": 1, "a": 1, "d": 1}
    full_mean, full_lo, full_hi, full_hw = boot_ci(items, lambda s: acc_full(s, lex, w))
    vs_lex = paired_delta_ci(items, lambda s: acc_full(s, lex, w), lambda s: acc_lexicon_only(s, lex))
    vs_mag = paired_delta_ci(items, lambda s: acc_full(s, lex, w), lambda s: acc_magnitude_only(s, lex))
    tw_mean, tw_p95 = twin_stats(items, lex, w)
    np95 = null_p95(items, lambda s: acc_full(s, lex, w))
    return {
        "n": len(items),
        "full_acc": round(full_mean, 4), "full_ci": [round(full_lo, 4), round(full_hi, 4)],
        "full_half_width": round(full_hw, 4),
        "lexicon_only_floor": round(acc_lexicon_only(items, lex), 4),
        "affector_magnitude_only_floor": round(acc_magnitude_only(items, lex), 4),
        "majority_floor": round(acc_majority(items), 4),
        "full_minus_lexicon": vs_lex,
        "full_minus_magnitude_only": vs_mag,
        "info_free_twin": {"mean": round(tw_mean, 4), "p95": round(tw_p95, 4),
                           "loses": full_lo > tw_p95},
        "null_p95": round(np95, 4),
        "ablation": ablation(items, lex),
        "weight_sweep": weight_sweep(items, lex),
    }


def main():
    out_dir = _out_dir()
    t0 = time.perf_counter()
    lex = build_force_lexicon()

    pops = {"SET_M_magnitude": SET_M, "SET_A_affordance": SET_A, "SET_D_directional": SET_D,
            "SET_L_letting": SET_L, "COMBINED": COMBINED, "HELDOUT": HELDOUT}
    blocks = {name: _pop_block(name, items, lex) for name, items in pops.items()}

    # LETTING block -- the 4th cue (Talmy causing-vs-letting) isolated by its ablation + the onset-cause guard.
    wl = {"m": 1, "a": 1, "d": 1, "e": 1}
    letting = {
        "n": len(SET_L),
        "full_acc": round(acc_full(SET_L, lex, wl), 4),
        "drop_letting_acc": round(acc_full(SET_L, lex, {"m": 1, "a": 1, "d": 1, "e": 0}), 4),
        "letting_lift": round(acc_full(SET_L, lex, wl) - acc_full(SET_L, lex, {"m": 1, "a": 1, "d": 1, "e": 0}), 4),
        "lexicon_only": round(acc_lexicon_only(SET_L, lex), 4),
        "full_minus_lexicon": paired_delta_ci(SET_L, lambda s: acc_full(s, lex, wl),
                                              lambda s: acc_lexicon_only(s, lex)),
        "heldout_letting_acc": round(acc_full(HELDOUT_L, lex, wl), 4),
        "onset_cause_negctrl": {f"{a}_{v}_{p}": type_with_full_tendency(a, v, p, c, True, lex)
                                for (a, v, p, c) in ONSET_CAUSE_NEGCTRL},
        "onset_cause_none_enable": all(type_with_full_tendency(a, v, p, c, True, lex) != "ENABLE"
                                       for (a, v, p, c) in ONSET_CAUSE_NEGCTRL),
        "note": ("ENABLE via restraint-remover (letting), CAUSE via strong force (causing); dropping the "
                 "letting cue collapses the ENABLE side (letting_lift). Onset-cause instruments (switch/"
                 "trigger/lever) are NOT typed ENABLE -- the causing-not-letting disambiguation guard."),
    }

    # positive-control minimal pairs
    pos = {}
    for name, pair in POS_CONTROL.items():
        w = {"m": 1, "a": 1, "d": 1}
        pos[name] = {
            "full": [type_with_full_tendency(a, v, p, c, True, lex) for (a, v, p, c, g) in pair],
            "lexicon_only": [force_dynamic_type(v, True, lex) for (a, v, p, c, g) in pair],
            "gold": [g for (a, v, p, c, g) in pair],
            "full_correct": all(type_with_full_tendency(a, v, p, c, True, lex) == g
                                for (a, v, p, c, g) in pair),
            "lexicon_correct": all(force_dynamic_type(v, True, lex) == g for (a, v, p, c, g) in pair),
        }

    # CONFLICT block -- the COMBINATION-RULE discriminator (additive force-sum vs single-cue WTA).
    w = {"m": 1, "a": 1, "d": 1}
    wta_accs = {c: round(acc_wta(CONFLICT, lex, c), 4) for c in ("m", "a", "d")}
    best_wta_cue = max(wta_accs, key=wta_accs.get)
    conflict = {
        "n": len(CONFLICT),
        "force_sum_acc": round(acc_full(CONFLICT, lex, w), 4),
        "single_cue_wta": wta_accs,
        "best_single_cue_wta": {"cue": best_wta_cue, "acc": wta_accs[best_wta_cue]},
        "lexicon_only": round(acc_lexicon_only(CONFLICT, lex), 4),
        "force_sum_minus_best_wta": paired_delta_ci(
            CONFLICT, lambda s: acc_full(s, lex, w), lambda s: acc_wta(s, lex, best_wta_cue)),
        "info_free_twin": (lambda t: {"mean": round(t[0], 4), "p95": round(t[1], 4),
                                      "loses": acc_full(CONFLICT, lex, w) > t[1]})(twin_stats(CONFLICT, lex, w)),
        "note": ("gold = net force sign (Wolff resultant); minority cue rotates evenly so NO single-cue rule "
                 "exceeds 8/12; only additive integration gets 12/12 -> proves the combination is a SUM, not WTA."),
    }

    cb = blocks["COMBINED"]
    ho = blocks["HELDOUT"]
    # PASS = full beats BOTH floors CI-separated on COMBINED, twin loses, held-out generalizes.
    beats_lex = cb["full_minus_lexicon"]["band"] == "ABOVE"
    beats_mag = cb["full_minus_magnitude_only"]["band"] == "ABOVE"
    twin_loses = cb["info_free_twin"]["loses"]
    heldout_ok = ho["full_minus_lexicon"]["band"] == "ABOVE" and ho["full_minus_magnitude_only"]["band"] == "ABOVE"
    passed = beats_lex and beats_mag and twin_loses and heldout_ok

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": ("FULL_PATIENT_TENDENCY_ESTIMATOR_BEATS_LEXICON_AND_MAGNITUDE_ONLY__TWIN_LOSES__GENERALIZES"
                    if passed else "FULL_ESTIMATOR_DID_NOT_CLEAR_ALL_GATES"),
        "summary": (
            f"FULL patient-tendency estimator (affector-magnitude + patient-affordance + directional, "
            f"Wolff force-sum) on COMBINED n={cb['n']}: {cb['full_acc']:.3f} "
            f"[{cb['full_ci'][0]:.3f},{cb['full_ci'][1]:.3f}] vs lexicon-only {cb['lexicon_only_floor']:.3f} "
            f"(+{cb['full_minus_lexicon']['delta']:.3f} {cb['full_minus_lexicon']['band']}) AND vs the PROVEN "
            f"affector-magnitude-only {cb['affector_magnitude_only_floor']:.3f} "
            f"(+{cb['full_minus_magnitude_only']['delta']:.3f} {cb['full_minus_magnitude_only']['band']}); "
            f"info-free twin mean {cb['info_free_twin']['mean']:.3f} p95 {cb['info_free_twin']['p95']:.3f} "
            f"(loses={cb['info_free_twin']['loses']}); null p95 {cb['null_p95']:.3f}. HELD-OUT n={ho['n']}: "
            f"{ho['full_acc']:.3f} beats magnitude-only +{ho['full_minus_magnitude_only']['delta']:.3f} "
            f"{ho['full_minus_magnitude_only']['band']}. Ablation(COMBINED): {cb['ablation']}. "
            f"Weight-sweep min {cb['weight_sweep']['min']:.3f} over {cb['weight_sweep']['n_configs']} configs. "
            f"PASS={passed}."),
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "populations": blocks,
        "conflict_combination_rule": conflict,
        "letting_causing_4th_cue": letting,
        "positive_control": pos,
        "mechanism": ("Wolff patient-side force sum: T = m + a + d over {affector-magnitude(abductive), "
                      "patient-affordance(core-physics disposition), directional/gravity(environmental O "
                      "force)}; sign(T)=concordance vs the affector(+endstate) -> ENABLE(tends)/CAUSE(resists). "
                      "Force-sum + concordance read-out PINNED Wolff 2007 / Wolff & Barbey 2015; affordance "
                      "property->sign map is OUR-INVENTION-UNDER-TEST gated on the twin + held-out + control."),
        "scope": ("Constructed cue-isolated minimal pairs, extraction GIVEN (as the proven demo + base typer "
                  "eval). Value = the full estimator types the magnitude-SILENT cases (affordance/directional) "
                  "the proven first term falls back to the verb on. Real-text auto-extraction is the follow-on."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"[verdict] {metrics['verdict']}")
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
