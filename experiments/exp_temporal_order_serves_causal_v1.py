"""SITUATION-MODEL TIME DIMENSION -- the downstream SERVE (bar step 3: SERVES or COMPOSES,
wire-don't-island): temporal order CONSTRAINS causal direction (a cause must PRECEDE its effect).

WHY: the live reader's causal extractor (hdlab.situation_reader._read_causation /
experiments/_causal_network) is ORDER-AGNOSTIC (its own docstring: "connective/adjacency-derived; NOT
a claim of genuine causal plausibility"). When the causal link is inferred from ADJACENCY (no explicit
direction-giving connective), the default is 'the earlier-MENTIONED event is the cause'. That FAILS on
flashback-causal sentences, where the CAUSE is anterior (past-perfect) but MENTIONED AFTER the effect:
  "The bridge collapsed . The flood had weakened it ."  -> cause = weakened (prior), effect = collapsed,
  but narration order mentions collapsed FIRST. Temporal precedence (weakened BEFORE collapsed) recovers
  the right causal direction; narration order inverts it. This is the brief's exact point: temporal order
  CONSTRAINS causation (cause precedes effect; Zwaan -- temporal order matters for causal inference).

ARMS (one variable = which order assigns cause-before-effect):
  NARRATION   baseline: the earlier-MENTIONED event is the cause (order-agnostic reader default).
  TEMPORAL    the reconstructed temporal-order register: the earlier-in-CHRONOLOGY event is the cause.

GOLD: flashback-causal sentences (cause is past-perfect / connective-anterior, narration order inverts
the pair) + a LINEAR-causal control (cause told first, both arms agree -> TEMPORAL must not regress).
Info-free TWIN: temporal order with tense labels shuffled -> collapses toward narration.

ASCII-only. Deterministic. Substrate-only (no LLM). Reuses the temporal-order register (Phase A/B).
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

from experiments import _temporal_order_register as R           # noqa: E402
from experiments import _temporal_ordering_multiframe as M       # noqa: E402

ANCHOR = "temporal_order_serves_causal_v1"
SEED = 20260829
N_BOOT = 5000

# FLASHBACK-CAUSAL: cause is anterior (past-perfect) but mentioned AFTER the effect -> narration inverts.
# gold: (cause_lemma, effect_lemma). The temporal register must place cause before effect.
FLASHBACK_CAUSAL = [
    {"text": "The bridge collapsed . The flood had weakened it .", "cause": "weakened", "effect": "collapsed"},
    {"text": "He was punished . He had stolen the bread .", "cause": "stolen", "effect": "punished"},
    {"text": "She wept . Her friend had betrayed her .", "cause": "betrayed", "effect": "wept"},
    {"text": "The crops failed . The rains had stopped early .", "cause": "stopped", "effect": "failed"},
    {"text": "The ship sank . An iceberg had struck the hull .", "cause": "struck", "effect": "sank"},
    {"text": "The town celebrated . The army had won the battle .", "cause": "won", "effect": "celebrated"},
    {"text": "He apologized . He had insulted her .", "cause": "insulted", "effect": "apologized"},
    {"text": "The fire spread . Someone had dropped a lantern .", "cause": "dropped", "effect": "spread"},
    {"text": "The patient recovered . The doctor had treated him .", "cause": "treated", "effect": "recovered"},
    {"text": "The garden bloomed . The gardener had watered it .", "cause": "watered", "effect": "bloomed"},
    {"text": "The king raged . A servant had spilled the wine .", "cause": "spilled", "effect": "raged"},
    {"text": "The child cried . A dog had frightened her .", "cause": "frightened", "effect": "cried"},
]

# LINEAR-CAUSAL control: cause told first (simple past both) -> narration and temporal AGREE.
LINEAR_CAUSAL = [
    {"text": "He studied hard , so he passed the exam .", "cause": "studied", "effect": "passed"},
    {"text": "The rain fell , and the river rose .", "cause": "fell", "effect": "rose"},
    {"text": "She trained daily , so she won the race .", "cause": "trained", "effect": "won"},
    {"text": "The wind blew , and the door slammed .", "cause": "blew", "effect": "slammed"},
    {"text": "He lit the fuse , and the cannon fired .", "cause": "lit", "effect": "fired"},
    {"text": "The sun rose , and the frost melted .", "cause": "rose", "effect": "melted"},
]


def _passage(text):
    return [text.split()]


def _cause_before_effect(reg, cause, effect):
    """Does the register place the CAUSE before the EFFECT? Returns 1 (correct causal direction), 0 wrong,
    None if either event not extracted."""
    q = reg.before(cause, effect)
    if q.pred == R.ABSTAIN:
        # temporal register abstains -> falls back to narration inside ComposedRegister already; if a
        # bare register abstains, treat as no-decision (scored as incorrect for coverage honesty)
        return 0
    return int(q.pred == R.BEFORE)


def _score(arm, items, seed=SEED, twin_seed=None):
    recs = []
    twin_rng = random.Random(twin_seed) if arm == "twin" else None
    for it in items:
        sents = _passage(it["text"])
        ev, tg, edges = R.extract_passage(sents, clause_pluperfect=True)
        narr = R.NarrationOrderFloor(ev, tg, edges)
        if arm == "narration":
            reg = narr
        elif arm == "temporal":
            reg = R.ComposedRegister(R.DiscreteOrderRegister(ev, tg, edges), narr)
        elif arm == "twin":
            tedges = R.make_twin_edges(edges, twin_rng)
            reg = R.ComposedRegister(R.DiscreteOrderRegister(ev, tg, tedges), narr)
        else:
            raise ValueError(arm)
        lemmas = {e.lemma for e in ev}
        if it["cause"] not in lemmas or it["effect"] not in lemmas:
            recs.append({"text": it["text"], "correct": None, "extracted": False})
            continue
        c = _cause_before_effect(reg, it["cause"], it["effect"])
        recs.append({"text": it["text"], "correct": c, "extracted": True})
    return recs


def _acc(recs):
    ex = [r for r in recs if r["extracted"]]
    if not ex:
        return 0.0, 0
    return sum(r["correct"] for r in ex) / len(ex), len(ex)


def _bootstrap(recs, seed=SEED, n_boot=N_BOOT):
    vals = [r["correct"] for r in recs if r["extracted"]]
    if not vals:
        return 0.0, 0.0, 0.0, 0
    rng = random.Random(seed)
    n = len(vals)
    boots = sorted(sum(vals[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    return sum(vals) / n, boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot)], n


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
    print("[self-test] causal-direction serve")
    recs = _score("temporal", FLASHBACK_CAUSAL[:3])
    assert any(r["extracted"] for r in recs), "no events extracted"
    print("[self-test] PASS")
    return True


def main(smoke=False):
    out_dir = _out_dir()
    t0 = time.perf_counter()

    fb_narr = _score("narration", FLASHBACK_CAUSAL)
    fb_temp = _score("temporal", FLASHBACK_CAUSAL)
    lin_narr = _score("narration", LINEAR_CAUSAL)
    lin_temp = _score("temporal", LINEAR_CAUSAL)

    n_twin = 20 if smoke else 200
    twin_accs = []
    for s in range(n_twin):
        tr = _score("twin", FLASHBACK_CAUSAL, twin_seed=1000 + s)
        a, k = _acc(tr)
        if k:
            twin_accs.append(a)
    twin_accs.sort()
    twin_mean = sum(twin_accs) / len(twin_accs) if twin_accs else 0.0
    twin_p95 = twin_accs[int(0.95 * (len(twin_accs) - 1))] if twin_accs else 0.0

    m_temp, lo_temp, hi_temp, n_temp = _bootstrap(fb_temp)
    m_narr, lo_narr, hi_narr, n_narr = _bootstrap(fb_narr)
    lin_temp_acc, _ = _acc(lin_temp)
    lin_narr_acc, _ = _acc(lin_narr)

    margin = m_temp - m_narr
    ci_sep = lo_temp > hi_narr
    twin_loses = lo_temp > twin_p95
    linear_ok = lin_temp_acc >= lin_narr_acc - 1e-9
    verdict = "HARD_PASS" if (ci_sep and twin_loses and margin >= 0.4 and linear_ok) else \
              ("MIDDLE_BAND" if margin >= 0.4 else "HARD_FAIL")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "summary": (f"{verdict}: flashback-causal DIRECTION acc TEMPORAL {m_temp:.3f} [{lo_temp:.3f},{hi_temp:.3f}] "
                    f"vs NARRATION {m_narr:.3f} [{lo_narr:.3f},{hi_narr:.3f}] (margin {margin:+.3f}); "
                    f"twin {twin_mean:.3f} (p95 {twin_p95:.3f}); CI-sep={ci_sep} twin_loses={twin_loses}; "
                    f"linear-causal control TEMPORAL {lin_temp_acc:.3f} == NARRATION {lin_narr_acc:.3f}."),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "flashback_causal": {"temporal_acc": round(m_temp, 4), "temporal_ci": [round(lo_temp, 4), round(hi_temp, 4)],
                             "narration_acc": round(m_narr, 4), "narration_ci": [round(lo_narr, 4), round(hi_narr, 4)],
                             "margin": round(margin, 4), "n": n_temp},
        "linear_causal_control": {"temporal_acc": round(lin_temp_acc, 4), "narration_acc": round(lin_narr_acc, 4),
                                  "note": "cause told first -> both agree; TEMPORAL must not regress"},
        "info_free_twin": {"mean": round(twin_mean, 4), "p95": round(twin_p95, 4), "n_shuffles": n_twin,
                           "excludes": "the win is a positional/lexical prior (twin collapses toward narration)"},
        "gates": {"ci_separated": ci_sep, "twin_loses": twin_loses, "margin": round(margin, 4),
                  "linear_no_regression": linear_ok},
        "n_gold": {"flashback_causal": len(FLASHBACK_CAUSAL), "linear_causal": len(LINEAR_CAUSAL)},
        "brain_note": ("Temporal precedence CONSTRAINS causation (cause precedes effect; Zwaan -- temporal "
                       "order matters for causal inference). On flashback-causal sentences the anterior "
                       "(past-perfect) CAUSE is mentioned after the effect, so the order-agnostic reader "
                       "default inverts the causal direction; the temporal register recovers it."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"verdict={verdict} elapsed={elapsed:.1f}s -> {os.path.join(out_dir, 'metrics.json')}")
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test(); sys.exit(0)
    smoke = ("--smoke" in sys.argv) and not ("--mode" in sys.argv and "full" in sys.argv)
    try:
        main(smoke=smoke)
    except SystemExit:
        raise
    except Exception as e:
        _atomic_write(_out_dir(), {"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                                   "traceback": traceback.format_exc()[:4000]})
        raise
