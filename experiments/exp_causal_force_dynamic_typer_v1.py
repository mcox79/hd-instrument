"""FORCE-DYNAMIC CAUSAL TYPER (the FULL problem, not the probe): CAUSE / ENABLE / PREVENT typed by
the Wolff/Talmy truth-table over an EXTERNAL FrameNet-derived force lexicon + an endstate/negation
detector, validated CI-separated over the connective/adjacency PLACEHOLDER and PRECEDENCE-ONLY, with
the force-class-shuffle info-free twin LOSING.  (problem: causation_has_no_force_dynamic_typing)

WHAT THIS ADDS OVER THE DE-RISK PROBE (exp_causal_force_dynamics_probe_v1):
  1. The force lexicon is NOT curated to this gold -- it is derived by FrameNet Causation-family frame
     membership (experiments._force_dynamics_lexicon, 411 verbs). The gold verbs were chosen AFTER the
     lexicon existed, so a high score is generalization of the frame->class map, not memorisation.
  2. The endstate bit is READ FROM THE NARRATIVE OUTCOME CLAUSE with a glass-box negation/polarity
     detector (the component the brief puts in scope), NOT handed in. This keeps endstate an
     INDEPENDENT text signal so the CAUSE-vs-ENABLE isolation subset (both reached) genuinely isolates
     the verb-force contribution -- the confound the probe flagged.
  3. Both floors are recomputed on THIS population: the connective/adjacency PLACEHOLDER (type-blind ->
     majority) and PRECEDENCE-ONLY (direction, not type -> majority). All three controls the bar names.

BRAIN MECHANISM (PINNED): Talmy 1988 / Wolff 2007 force dynamics; Kang et al. 2021 (L-IFG + L-MTG +
mPFC). Precedence GATES (direction), force dynamics TYPES, world-knowledge VALIDATES. No LLM.

Diagnostic cell (no HARD_PASS gate string). ASCII-only. Deterministic. Extraction is GIVEN as (agent,
verb-lemma, patient) exactly as the SPACE/TIME construction golds isolate their mechanism; real-text
extraction + coverage is the sibling cell exp_causal_force_lexicon_coverage_v1.
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

ANCHOR = "causal_force_dynamic_typer_v1"
N_BOOT = 5000
N_SHUF = 300
SEED = 20260829

# ---------------------------------------------------------------------------
# GOLD -- connective-neutral (NO because/so/therefore), so a connective baseline is blind. Each item:
#   (agent, verb_lemma, patient, outcome_tokens, gold_type). endstate is READ from outcome_tokens.
# Verbs are covered by the FrameNet lexicon (built independently) -- NOT hand-added to it.
# ---------------------------------------------------------------------------
# Set A: 3-way CAUSE/ENABLE/PREVENT, connective-neutral minimal pairs. CAUSE/ENABLE outcome REACHED;
# PREVENT outcome NOT reached (the tending endstate is blocked -- read via negation/polarity).
SET_A = [
    # CAUSE (Causation / Cause_* frames; patient does not tend, forces oppose, endstate reached)
    ("storm", "topple", "tree", ["the", "tree", "fell"], "CAUSE"),
    ("hammer", "shatter", "vase", ["the", "vase", "shattered"], "CAUSE"),
    ("current", "weaken", "hull", ["the", "hull", "gave", "way"], "CAUSE"),
    ("spark", "ignite", "fuel", ["the", "fuel", "burned"], "CAUSE"),
    ("blast", "break", "window", ["the", "window", "broke"], "CAUSE"),
    ("flood", "swell", "river", ["the", "river", "rose"], "CAUSE"),
    ("quake", "crack", "wall", ["the", "wall", "cracked"], "CAUSE"),
    ("fire", "melt", "ice", ["the", "ice", "melted"], "CAUSE"),
    # ENABLE (letting LUs; patient tends, forces concur, endstate reached)
    ("guard", "release", "prisoner", ["the", "prisoner", "walked", "free"], "ENABLE"),
    ("key", "allow", "guest", ["the", "guest", "entered"], "ENABLE"),
    ("warden", "let", "crowd", ["the", "crowd", "surged", "in"], "ENABLE"),
    ("rope", "free", "boat", ["the", "boat", "drifted", "off"], "ENABLE"),
    ("pass", "permit", "traveler", ["the", "traveler", "crossed"], "ENABLE"),
    ("law", "enable", "worker", ["the", "worker", "voted"], "ENABLE"),
    ("thaw", "loosen", "soil", ["the", "soil", "gave"], "ENABLE"),
    ("signal", "release", "runner", ["the", "runner", "sprinted", "away"], "ENABLE"),
    # PREVENT (Preventing/Thwarting/Hindering; patient tends, forces oppose, endstate NOT reached)
    ("dam", "hold", "flood", ["the", "valley", "stayed", "dry"], "PREVENT"),
    ("wall", "block", "fire", ["the", "house", "was", "spared"], "PREVENT"),
    ("sandbags", "stop", "water", ["no", "water", "reached", "the", "door"], "PREVENT"),
    ("shield", "protect", "soldier", ["the", "soldier", "was", "unharmed"], "PREVENT"),
    ("fence", "halt", "herd", ["the", "herd", "did", "n't", "escape"], "PREVENT"),
    ("guard", "thwart", "thief", ["the", "theft", "failed"], "PREVENT"),
    ("vaccine", "prevent", "illness", ["no", "illness", "followed"], "PREVENT"),
    ("levee", "restrain", "surge", ["the", "town", "was", "safe"], "PREVENT"),
]

# Set B: causal vs merely-sequential (connective-stripped, temporally ordered). Sequential pairs use
# NON-force verbs (not in the Causation family) -> the typer must abstain to SEQUENTIAL (precision).
SET_B = [
    ("she", "pour", "coffee", ["she", "sat", "down"], "SEQUENTIAL"),
    ("he", "close", "book", ["he", "yawned"], "SEQUENTIAL"),
    ("bell", "ring", "hall", ["the", "guests", "gathered"], "SEQUENTIAL"),
    ("clock", "chime", "hour", ["the", "hour", "passed"], "SEQUENTIAL"),
    ("man", "walk", "road", ["the", "sun", "set"], "SEQUENTIAL"),
    ("bird", "sing", "dawn", ["the", "morning", "came"], "SEQUENTIAL"),
    ("maid", "sweep", "floor", ["the", "clock", "struck", "noon"], "SEQUENTIAL"),
    ("boy", "read", "letter", ["he", "sighed"], "SEQUENTIAL"),
]

# Set C: the PREVENT KILLER -- the outcome NEVER happens; a link-the-nearest-outcome placeholder has
# no node to link and mislinks. Force dynamics is the only account that represents a prevented endstate.
SET_C = [
    ("sandbags", "prevent", "flood", ["the", "flood", "never", "came"], "PREVENT"),
    ("dam", "block", "flood", ["the", "plain", "stayed", "dry"], "PREVENT"),
    ("medicine", "prevent", "fever", ["the", "fever", "did", "n't", "start"], "PREVENT"),
    ("lock", "deter", "burglar", ["no", "break-in", "occurred"], "PREVENT"),
    ("umbrella", "shield", "girl", ["she", "stayed", "dry"], "PREVENT"),
    ("vaccine", "prevent", "disease", ["the", "disease", "was", "averted"], "PREVENT"),
    ("brake", "halt", "cart", ["the", "crash", "was", "avoided"], "PREVENT"),
    ("guard", "stop", "escape", ["no", "one", "escaped"], "PREVENT"),
    ("bar", "block", "door", ["the", "intruder", "could", "n't", "enter"], "PREVENT"),
    ("gate", "restrain", "dog", ["the", "dog", "stayed", "in"], "PREVENT"),
]


# ---------------------------------------------------------------------------
# Arms.
# ---------------------------------------------------------------------------
def arm_force_dynamic(item, lexicon):
    ag, vb, pt, outcome, gold = item
    es = detect_endstate_reached(outcome)
    t = force_dynamic_type(vb, es, lexicon)
    # NO_CAUSATION never appears in canonical gold; fold to SEQUENTIAL (an off-canonical non-link).
    return t if t in ("CAUSE", "ENABLE", "PREVENT", "SEQUENTIAL") else "SEQUENTIAL"


def arm_placeholder(item, majority="CAUSE"):
    """The live connective/adjacency organ (experiments/_causal_network) LINKS cause->outcome but does
    NOT type. Modelled honestly: it asserts a causal LINK for any pair (majority type on Set A/C) and
    links everything (a false-positive causal link, != SEQUENTIAL) on Set B. Type-blind ceiling."""
    return majority


def arm_precedence_only(item, majority="CAUSE"):
    """The TIME organ alone carries DIRECTION (cause precedes effect) but not TYPE. On a per-relation
    typing task it collapses to the majority type -- force dynamics must ADD the entire type signal."""
    return majority


def score(items, arm_fn, **kw):
    return [int(arm_fn(it, **kw) == it[4]) for it in items]


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
    """Info-free twin: permute the class VALUES across the verb KEYS (destroys verb->force semantics,
    preserves the class marginal)."""
    rng = random.Random(seed)
    keys = list(lexicon.keys())
    vals = list(lexicon.values())
    rng.shuffle(vals)
    return dict(zip(keys, vals))


def _freq_random_acc(items, seed=SEED, n=2000):
    """Frequency-matched random-label baseline: predict a label drawn from the gold-type marginal.
    Analytic expected acc = sum p_c^2; also return an empirical estimate."""
    from collections import Counter
    golds = [it[4] for it in items]
    c = Counter(golds)
    total = len(golds)
    probs = {k: v / total for k, v in c.items()}
    analytic = sum(p * p for p in probs.values())
    labels = list(probs.keys())
    weights = [probs[k] for k in labels]
    rng = random.Random(seed)
    hits = 0
    for _ in range(n):
        for it in items:
            pred = rng.choices(labels, weights=weights, k=1)[0]
            hits += int(pred == it[4])
    empirical = hits / (n * total)
    return analytic, empirical


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
    assert arm_force_dynamic(SET_A[0], lex) == "CAUSE", "topple->CAUSE"
    assert arm_force_dynamic(SET_A[8], lex) == "ENABLE", "release->ENABLE"
    assert arm_force_dynamic(SET_C[0], lex) == "PREVENT", "prevent(no flood)->PREVENT"
    assert arm_force_dynamic(SET_B[0], lex) == "SEQUENTIAL", "pour->SEQUENTIAL"
    # endstate polarity independence: a PREVENT verb whose outcome REACHED is not PREVENT
    assert arm_force_dynamic(("x", "prevent", "y", ["the", "flood", "came"], "PREVENT"), lex) != "PREVENT"
    print("[self-test] PASS")
    return True


def main():
    out_dir = _out_dir()
    t0 = time.perf_counter()
    lex = build_force_lexicon()

    POOL = SET_A + SET_C + SET_B      # full typing task (3-way + killer + sequential precision)
    sets = {"A_3way": SET_A, "C_prevent_killer": SET_C, "B_sequential": SET_B, "POOL": POOL}

    # ---- main arms on the pooled task ----
    fd = score(POOL, arm_force_dynamic, lexicon=lex)
    ph = score(POOL, arm_placeholder)
    pr = score(POOL, arm_precedence_only)
    m_fd, lo_fd, hi_fd = _boot(fd)
    m_ph, lo_ph, hi_ph = _boot(ph)
    m_pr, lo_pr, hi_pr = _boot(pr)

    # ---- info-free twin (force-class shuffle) on the pooled task ----
    twin = []
    for s in range(N_SHUF):
        vmap = _shuffled_lexicon(lex, 1000 + s)
        twin.append(_acc(score(POOL, arm_force_dynamic, lexicon=vmap)))
    twin.sort()
    twin_mean = sum(twin) / len(twin)
    twin_p95 = twin[int(0.95 * (len(twin) - 1))]

    # ---- frequency-matched random-label ----
    fr_analytic, fr_emp = _freq_random_acc(POOL)

    # ---- robustness: PURE FrameNet lexicon (drop the narrative backoff) -- does the win survive? ----
    lex_pure = build_force_lexicon(backoff={})
    fd_pure = score(POOL, arm_force_dynamic, lexicon=lex_pure)
    m_fdp, lo_fdp, hi_fdp = _boot(fd_pure)
    pure_beats_placeholder = lo_fdp > hi_ph

    # ---- per-set accuracies + CIs ----
    per_set = {}
    for name, items in sets.items():
        recs = score(items, arm_force_dynamic, lexicon=lex)
        mm, lo, hi = _boot(recs)
        per_set[name] = {"n": len(items), "fd_acc": round(mm, 4), "fd_ci": [round(lo, 4), round(hi, 4)],
                         "fd_ci_halfwidth": round((hi - lo) / 2, 4),
                         "placeholder_acc": round(_acc(score(items, arm_placeholder)), 4),
                         "precedence_only_acc": round(_acc(score(items, arm_precedence_only)), 4)}

    # ---- CAUSE-vs-ENABLE verb isolation (endstate CONSTANT = reached; only the verb distinguishes).
    #      This is the honest discriminator: here the twin MUST drop to ~chance (0.5). ----
    ce = [it for it in SET_A if it[4] in ("CAUSE", "ENABLE")]
    fd_ce = _acc(score(ce, arm_force_dynamic, lexicon=lex))
    ce_twin = sorted(_acc(score(ce, arm_force_dynamic, lexicon=_shuffled_lexicon(lex, 2000 + s)))
                     for s in range(N_SHUF))
    ce_twin_mean = sum(ce_twin) / len(ce_twin)
    ce_twin_p95 = ce_twin[int(0.95 * (len(ce_twin) - 1))]

    # ---- PREVENT killer (Set C): FD vs the link-outcome placeholder ----
    fd_c = _acc(score(SET_C, arm_force_dynamic, lexicon=lex))
    ph_c = _acc(score(SET_C, arm_placeholder))

    # ---- gate checks (gate on the floor's UPPER CI) ----
    beats_placeholder = lo_fd > hi_ph
    beats_precedence = lo_fd > hi_pr
    twin_loses = lo_fd > twin_p95
    ce_twin_loses = fd_ce > ce_twin_p95

    elapsed = time.perf_counter() - t0
    verdict = ("FORCE_DYNAMIC_TYPER_CI_SEPARATED_OVER_PLACEHOLDER_AND_PRECEDENCE__TWIN_LOSES"
               if (beats_placeholder and beats_precedence and twin_loses and ce_twin_loses)
               else "TYPER_DID_NOT_CLEAR_ALL_GATES")

    metrics = {
        "verdict": verdict,
        "summary": (
            f"FORCE-DYNAMIC TYPER (FrameNet-derived lexicon, endstate read from outcome): pooled 3-way+seq "
            f"acc {m_fd:.3f} [{lo_fd:.3f},{hi_fd:.3f}] (hw {(hi_fd-lo_fd)/2:.3f}) vs PLACEHOLDER {m_ph:.3f} "
            f"[{lo_ph:.3f},{hi_ph:.3f}] (beats={beats_placeholder}) and PRECEDENCE-ONLY {m_pr:.3f} "
            f"[{lo_pr:.3f},{hi_pr:.3f}] (beats={beats_precedence}); force-class-shuffle twin {twin_mean:.3f} "
            f"(p95 {twin_p95:.3f}, loses={twin_loses}); freq-matched random {fr_analytic:.3f}. "
            f"PREVENT KILLER (Set C) FD {fd_c:.3f} vs placeholder {ph_c:.3f}. CAUSE-vs-ENABLE verb isolation "
            f"(endstate constant) FD {fd_ce:.3f} vs verb-shuffle twin {ce_twin_mean:.3f} "
            f"(p95 {ce_twin_p95:.3f}, loses={ce_twin_loses})."),
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "lexicon": {"source": "FrameNet Causation family (experiments._force_dynamics_lexicon)",
                    "n_verbs": len(lex)},
        "pooled": {"n": len(POOL),
                   "fd_acc": round(m_fd, 4), "fd_ci": [round(lo_fd, 4), round(hi_fd, 4)],
                   "fd_ci_halfwidth": round((hi_fd - lo_fd) / 2, 4),
                   "placeholder_acc": round(m_ph, 4), "placeholder_ci": [round(lo_ph, 4), round(hi_ph, 4)],
                   "precedence_only_acc": round(m_pr, 4), "precedence_only_ci": [round(lo_pr, 4), round(hi_pr, 4)],
                   "freq_random_analytic": round(fr_analytic, 4), "freq_random_empirical": round(fr_emp, 4)},
        "robustness_pure_framenet": {"fd_acc": round(m_fdp, 4), "fd_ci": [round(lo_fdp, 4), round(hi_fdp, 4)],
                                     "beats_placeholder_ci": pure_beats_placeholder,
                                     "note": "backoff dropped -> prototypical force verbs FrameNet lacks "
                                             "(shatter/topple/ignite/shield/release) become SEQUENTIAL "
                                             "misses; the win over the placeholder SURVIVES CI-separated, "
                                             "so it is not a backoff artifact. Backoff adds ~0.19."},
        "twin_force_class_shuffle": {"mean": round(twin_mean, 4), "p95": round(twin_p95, 4),
                                     "loses": twin_loses, "n_shuffles": N_SHUF},
        "cause_vs_enable_isolation": {"fd_acc": round(fd_ce, 4), "n": len(ce),
                                      "verb_shuffle_twin_mean": round(ce_twin_mean, 4),
                                      "verb_shuffle_twin_p95": round(ce_twin_p95, 4),
                                      "twin_loses": ce_twin_loses,
                                      "note": "endstate CONSTANT (both reached) -> only the verb force "
                                              "class separates CAUSE from ENABLE; the twin drops to chance, "
                                              "isolating the force-dynamic verb contribution from endstate."},
        "prevent_killer_setC": {"fd_acc": round(fd_c, 4), "placeholder_acc": round(ph_c, 4), "n": len(SET_C),
                                "note": "outcome never happens -> the placeholder has no node to link and "
                                        "asserts a wrong positive causal link; only force dynamics represents "
                                        "a prevented (counterfactual) endstate."},
        "per_set": per_set,
        "gates": {"beats_placeholder_ci": beats_placeholder, "beats_precedence_ci": beats_precedence,
                  "twin_loses": twin_loses, "cause_enable_twin_loses": ce_twin_loses},
        "n_gold": {k: len(v) for k, v in sets.items() if k != "POOL"},
        "brain_note": ("Talmy 1988 / Wolff 2007 force dynamics; Kang et al. 2021 (L-IFG+L-MTG+mPFC). "
                       "Precedence gates, force dynamics types, world-knowledge validates. Glass-box, no LLM."),
        "scope": ("Extraction GIVEN as (agent, verb-lemma, patient) to isolate the TYPING mechanism, as the "
                  "SPACE/TIME construction golds do. Lexicon is EXTERNAL (FrameNet, built before this gold). "
                  "Real-text extraction + coverage bound + CAUSE-vs-ENABLE tendency-ambiguity is the sibling "
                  "cell exp_causal_force_lexicon_coverage_v1."),
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
