"""exp_generalize_causation_typer_maven_ere_v1 -- GENERALIZATION rerun of the CAUSATION TYPER cluster on a
large pre-existing annotated causal corpus (MAVEN-ERE, Wang et al. EMNLP 2022).

WHICH ORGANS. The two genuinely-fragile causation typers whose headlines rest on constructed minimal pairs:
  - causation_has_no_force_dynamic_typing      (0.929 on n=42 connective-neutral minimal pairs)
  - causation_typing_needs_a_patient_tendency_estimator (1.000 on n=40 tendency-ambiguous minimal pairs)
Both share the claim: a glass-box FORCE-DYNAMIC typer (Talmy/Wolff CAUSE/ENABLE/PREVENT truth-table over a
FrameNet-derived verb lexicon) distinguishes causal SUB-TYPES better than a connective/majority placeholder.
Their only real-text checks were tiny solver-adjudicated point estimates (n=13 / n=21). A SIBLING organ,
causation_is_typed_per_clause, already ran a real LitBank test and the typer LOST to majority-CAUSE
(0.158 vs 0.842, n=19). This reruns the SAME force-dynamic typer (imported verbatim from
experiments._force_dynamics_lexicon) on a LARGE, independently-annotated causal corpus.

THE POPULATION. MAVEN-ERE valid split (710 docs), gold causal_relations = {CAUSE, PRECONDITION}. Each
relation links a CAUSING event to an effect event (both annotated as REACHED). PRECONDITION ~= ENABLE
(a necessary enabling condition). So this is the real-text CAUSE-vs-ENABLE test (no PREVENT: causal
relations are positive), n = all gold causal relations.

WHAT WE MEASURE (brain-foundational + honest generalization, mirroring the retrieval rerun's structure):
  1. FIRE RATE: on real causal relations, how often is the CAUSING event's trigger even a force-dynamic verb
     (the typer's required input)? A typer that needs a causal connective verb may rarely fire on annotated
     event-event causality -> low real-text coverage regardless of accuracy where it fires.
  2. ACCURACY WHERE IT FIRES: CAUSE-vs-ENABLE hit vs the strongest floor = MAJORITY class (predict CAUSE
     always; recomputed on the fired subset).
  3. INFO-FREE TWIN: shuffle the lexicon's class labels (same fire rate, no real force information) -> LOSE.
  4. COVERAGE-WEIGHTED value = fire_rate * (accuracy - majority_floor) -- the deployed contribution.
HOLDS = typer beats majority CI-separated on a non-trivial fired subset, twin losing. Real hdlab-adjacent
force lexicon (FrameNet). NO external LLM. CPU. ASCII-only. Deterministic.

Run: .venv/Scripts/python.exe experiments/exp_generalize_causation_typer_maven_ere_v1.py --self-test
     ... --full
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._force_dynamics_lexicon import build_force_lexicon  # noqa: E402

ANCHOR = "generalize_causation_typer_maven_ere_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
MAVEN_VALID = os.path.join(REPO, "data", "benchmark_trap_check", "maven_ere", "valid.jsonl")

_LEMM = None


def _lemmatize(w):
    """Verb lemma via WordNet (the lexicon keys are lemmas). Falls back to lowercase."""
    global _LEMM
    if _LEMM is None:
        from nltk.stem import WordNetLemmatizer
        _LEMM = WordNetLemmatizer()
    w = str(w).lower().strip()
    try:
        return _LEMM.lemmatize(w, pos="v")
    except Exception:
        return w


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_causal_relations(path):
    """Return list of (cause_trigger_lemma, effect_trigger_lemma, gold) where gold in {CAUSE, ENABLE}.
    MAVEN causal_relations: {'CAUSE': [[e1,e2],...], 'PRECONDITION': [[e1,e2],...]}. e1 is the causing
    event. PRECONDITION -> ENABLE (a necessary enabling condition)."""
    rels = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            trig = {}
            for ev in d.get("events", []):
                m = ev.get("mention") or []
                if m:
                    trig[ev["id"]] = m[0].get("trigger_word", "")
            cr = d.get("causal_relations", {}) or {}
            for label, gold in (("CAUSE", "CAUSE"), ("PRECONDITION", "ENABLE")):
                for pair in cr.get(label, []):
                    e1, e2 = pair[0], pair[1]
                    if e1 in trig and e2 in trig:
                        rels.append((_lemmatize(trig[e1]), _lemmatize(trig[e2]), gold))
    return rels


def type_relation(cause_lemma, lex):
    """Force-dynamic class of the CAUSING event's trigger. CAUSE/ENABLE -> a 2-way causal-subtype
    prediction; PREVENT-class in a positive causal relation is anomalous (map to CAUSE, its nearest
    positive-causal reading); not-in-lexicon -> None (typer does not fire)."""
    cls = lex.get(cause_lemma)
    if cls is None:
        return None
    if cls == "ENABLE":
        return "ENABLE"
    return "CAUSE"  # CAUSE or PREVENT class -> positive-causal prediction = CAUSE


def evaluate(rels, lex, gen_np, n_boot=2000):
    fired = [(c, e, g) for (c, e, g) in rels if type_relation(c, lex) is not None]
    n_all, n_fire = len(rels), len(fired)
    fire_rate = n_fire / max(1, n_all)
    if n_fire == 0:
        return {"fire_rate": 0.0, "n_all": n_all, "n_fire": 0}
    preds = [type_relation(c, lex) for (c, e, g) in fired]
    gold = [g for (c, e, g) in fired]
    correct = np.array([int(p == gld) for p, gld in zip(preds, gold)], dtype=np.float64)
    # majority floor on the FIRED subset (predict the majority gold class always)
    maj_class = collections.Counter(gold).most_common(1)[0][0]
    maj_correct = np.array([int(maj_class == gld) for gld in gold], dtype=np.float64)
    # info-free twin: shuffle the lexicon class labels -> same fire set, permuted classes
    lex_keys = sorted(lex.keys())
    perm_vals = list(lex.values())
    gen_np.shuffle(perm_vals)
    twin_lex = {k: v for k, v in zip(lex_keys, perm_vals)}
    twin_preds = [type_relation(c, twin_lex) if type_relation(c, twin_lex) else "CAUSE" for (c, e, g) in fired]
    twin_correct = np.array([int(p == gld) for p, gld in zip(twin_preds, gold)], dtype=np.float64)

    def ci(v):
        idx = np.array([gen_np.integers(0, len(v), size=len(v)) for _ in range(n_boot)])
        b = v[idx].mean(axis=1)
        return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

    def paired(a, b):
        diff = a - b
        idx = np.array([gen_np.integers(0, len(diff), size=len(diff)) for _ in range(n_boot)])
        bt = diff[idx].mean(axis=1)
        lo, hi = float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))
        null = np.array([np.abs((diff * gen_np.choice([-1.0, 1.0], size=len(diff))).mean()) for _ in range(n_boot)])
        p95 = float(np.percentile(null, 95))
        band = "ABOVE" if lo > 0 and lo > p95 else ("BELOW" if hi < 0 else "NOT_SEP")
        return {"delta": float(diff.mean()), "lo": lo, "hi": hi, "null_p95": p95, "band": band}

    acc, alo, ahi = ci(correct)
    maj, mlo, mhi = ci(maj_correct)
    return {"n_all": n_all, "n_fire": n_fire, "fire_rate": fire_rate,
            "gold_dist_fired": dict(collections.Counter(gold)),
            "typer_acc": {"mean": acc, "lo": alo, "hi": ahi},
            "majority_floor": {"mean": maj, "lo": mlo, "hi": mhi, "class": maj_class},
            "twin_acc": float(twin_correct.mean()),
            "typer_minus_majority": paired(correct, maj_correct),
            "typer_minus_twin": paired(correct, twin_correct),
            "coverage_weighted_lift": fire_rate * (acc - maj)}


def run(n_boot=2000):
    t0 = time.perf_counter()
    lex = build_force_lexicon()
    rels = load_causal_relations(MAVEN_VALID)
    gold_all = collections.Counter(g for (_, _, g) in rels)
    gen = np.random.default_rng(20260830)
    res = evaluate(rels, lex, gen, n_boot)
    res["gold_dist_all"] = dict(gold_all)
    res["lexicon_size"] = len(lex)
    verdict = "HOLDS"
    tm = res.get("typer_minus_majority", {})
    if res["fire_rate"] < 0.15 or tm.get("band") != "ABOVE":
        verdict = "DOES_NOT_HOLD"
    res["VERDICT"] = verdict
    res["meta"] = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0}
    _log("causal relations n=%d gold=%s | lexicon=%d" % (res["n_all"], res["gold_dist_all"], len(lex)))
    _log("FIRE RATE = %.3f (%d/%d causal relations have a force-dynamic causing verb)"
         % (res["fire_rate"], res["n_fire"], res["n_all"]))
    _log("typer acc (where fires) = %.3f [%.3f,%.3f] | MAJORITY floor = %.3f (%s) | twin = %.3f"
         % (res["typer_acc"]["mean"], res["typer_acc"]["lo"], res["typer_acc"]["hi"],
            res["majority_floor"]["mean"], res["majority_floor"]["class"], res["twin_acc"]))
    _log("typer - majority = %+.3f [%.3f,%.3f] %s | typer - twin = %+.3f %s"
         % (tm["delta"], tm["lo"], tm["hi"], tm["band"],
            res["typer_minus_twin"]["delta"], res["typer_minus_twin"]["band"]))
    _log("coverage-weighted lift = %+.4f | VERDICT = %s" % (res["coverage_weighted_lift"], verdict))
    return res


def self_test():
    _log("SELF-TEST: MAVEN valid loads; causal relations non-empty; lexicon builds")
    lex = build_force_lexicon()
    assert len(lex) > 200, "lexicon too small: %d" % len(lex)
    rels = load_causal_relations(MAVEN_VALID)
    assert len(rels) > 1000, "expected >1000 causal relations, got %d" % len(rels)
    golds = set(g for (_, _, g) in rels)
    assert golds == {"CAUSE", "ENABLE"}, "unexpected gold set: %s" % golds
    _log("  n_causal=%d gold=%s lexicon=%d" % (len(rels), dict(collections.Counter(g for *_, g in rels)), len(lex)))
    _log("SELF-TEST: typer maps a known CAUSE verb and abstains on a non-force verb")
    assert type_relation(_lemmatize("shatter"), lex) == "CAUSE", "shatter should be CAUSE-class"
    assert type_relation("zzznotaverb", lex) is None, "unknown verb should not fire"
    _log("SELF-TEST PASS")
    return {"n_causal": len(rels), "lexicon": len(lex)}


def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()
    if args.self_test or not args.full:
        st = self_test()
        _atomic_write(os.path.join(OUTPUT_DIR, "_self_test", "metrics.json"),
                      {"verdict": "SELFTEST_PASS", "selftest": st, "ts_iso": _now_iso()})
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return
    res = run()
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), res)
    _log("DONE full in %.1fs -> %s" % (time.perf_counter() - t0, OUTPUT_DIR))


if __name__ == "__main__":
    main()
