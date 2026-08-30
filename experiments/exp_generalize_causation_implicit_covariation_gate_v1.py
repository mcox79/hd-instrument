"""exp_generalize_causation_implicit_covariation_gate_v1 -- the empirical GATE for the causation reframe
(research_causation_typer_wall_implicit_and_mental_causation_2026-08-30.md).

WHY. RERUN 2 (exp_generalize_causation_typer_maven_ere_v1) found the force-dynamic causation typer DOES NOT
HOLD on real MAVEN-ERE: fires on 16.1% of causal relations, and where it fires its force-class signal is
indistinguishable from a shuffled-lexicon twin (+0.018 NOT_SEP). The research drill's PINNED verdict: real
narrative causation is a WHOLE-EVENT causal-GRAPH property inferred by a different brain system
(Trabasso/van den Broek causal-network; Kintsch construction-integration; Mason & Just 2004 fMRI), NOT a
verb-internal force computation. So the reframe is: the operative signal is EVENT-TYPE COVARIATION /
world-knowledge ("does event-type A tend to cause event-type B?"), a glass-box selectional-preference
scorer -- the dual-route covariation mechanism (Griffiths & Tenenbaum structure inference; Fugelsang &
Dunbar 2005; Kuperberg 2011 connective-free N400).

THE GATE (symmetric with the retrieval similar-competitor gate): does the IMPLICIT event-type-covariation
route carry the causal-type signal that the FORCE-DYNAMIC route lacks? Learn P(label | cause_type,
effect_type) from MAVEN TRAIN (a pure co-occurrence count, glass-box, no LLM); predict the CAUSE-vs-
PRECONDITION type on VALID; compare against (a) the force-dynamic typer (RERUN 2: +0.018 twin, no signal),
(b) the majority floor, and (c) the covariation model's OWN shuffled-type-pair twin. The decisive contrast:
force-dynamics ~ its twin (no signal), covariation > its twin CI-separated (real signal) -> the missing
mechanism is implicit event-type covariation, empirically, not force-dynamics. Reports coverage on the
83.9% subset the typer never fires on. NO external LLM. CPU. ASCII-only. Deterministic.

Run: .venv/Scripts/python.exe experiments/exp_generalize_causation_implicit_covariation_gate_v1.py --self-test
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
from experiments import exp_generalize_causation_typer_maven_ere_v1 as CAUS  # noqa: E402

ANCHOR = "generalize_causation_implicit_covariation_gate_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
TRAIN = os.path.join(REPO, "data", "benchmark_trap_check", "maven_ere", "train.jsonl")
VALID = os.path.join(REPO, "data", "benchmark_trap_check", "maven_ere", "valid.jsonl")


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_typed_relations(path):
    """(cause_type, effect_type, cause_trigger_lemma, gold in {CAUSE,ENABLE})."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            typ, trig = {}, {}
            for ev in d.get("events", []):
                typ[ev["id"]] = ev.get("type", "?")
                m = ev.get("mention") or []
                trig[ev["id"]] = m[0].get("trigger_word", "") if m else ""
            cr = d.get("causal_relations", {}) or {}
            for label, gold in (("CAUSE", "CAUSE"), ("PRECONDITION", "ENABLE")):
                for a, b in cr.get(label, []):
                    if a in typ and b in typ:
                        out.append((typ[a], typ[b], CAUS._lemmatize(trig[a]), gold))
    return out


def learn_typepair_model(train_rels, min_count=5):
    """P(label | cause_type, effect_type) from TRAIN counts. Glass-box co-occurrence; backoff to the
    global majority for pairs seen < min_count (a pure covariation/selectional-preference scorer)."""
    ct = collections.defaultdict(lambda: collections.Counter())
    glob = collections.Counter()
    for (cty, ety, _lem, g) in train_rels:
        ct[(cty, ety)][g] += 1
        glob[g] += 1
    majority = glob.most_common(1)[0][0]
    model = {}
    for pair, cnt in ct.items():
        if sum(cnt.values()) >= min_count:
            model[pair] = cnt.most_common(1)[0][0]
    return model, majority


def evaluate(valid_rels, model, majority, lex, gen_np, n_boot=2000):
    n = len(valid_rels)
    gold = np.array([1 if g == "ENABLE" else 0 for (_, _, _, g) in valid_rels])
    # covariation prediction (backoff to majority for unseen pairs)
    cov_pred = [model.get((c, e), majority) for (c, e, _l, _g) in valid_rels]
    cov_correct = np.array([int(p == g) for p, (_, _, _, g) in zip(cov_pred, valid_rels)], dtype=np.float64)
    covered = np.array([1 if (c, e) in model else 0 for (c, e, _l, _g) in valid_rels])
    # majority floor
    maj_correct = np.array([int(majority == g) for (_, _, _, g) in valid_rels], dtype=np.float64)
    # force-dynamic typer (fires on the causing verb; abstain->majority so it is a fair full-population arm)
    fd_pred = [CAUS.type_relation(l, lex) or majority for (_, _, l, _g) in valid_rels]
    fd_correct = np.array([int(p == g) for p, (_, _, _, g) in zip(fd_pred, valid_rels)], dtype=np.float64)
    fd_fires = np.array([1 if CAUS.type_relation(l, lex) is not None else 0 for (_, _, l, _g) in valid_rels])
    # covariation's OWN info-free twin: shuffle the type-pair -> label mapping
    keys = sorted(model.keys())
    vals = [model[k] for k in keys]
    gen_np.shuffle(vals)
    twin_model = {k: v for k, v in zip(keys, vals)}
    twin_pred = [twin_model.get((c, e), majority) for (c, e, _l, _g) in valid_rels]
    twin_correct = np.array([int(p == g) for p, (_, _, _, g) in zip(twin_pred, valid_rels)], dtype=np.float64)

    def paired(a, b):
        diff = a - b
        idx = np.array([gen_np.integers(0, len(diff), size=len(diff)) for _ in range(n_boot)])
        bt = diff[idx].mean(axis=1)
        lo, hi = float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))
        null = np.array([np.abs((diff * gen_np.choice([-1.0, 1.0], size=len(diff))).mean()) for _ in range(n_boot)])
        p95 = float(np.percentile(null, 95))
        band = "ABOVE" if lo > 0 and lo > p95 else ("BELOW" if hi < 0 else "NOT_SEP")
        return {"delta": float(diff.mean()), "lo": lo, "hi": hi, "null_p95": p95, "band": band}

    # on the subset where the FORCE-DYNAMIC typer does NOT fire (83.9%): does covariation carry signal?
    nf = fd_fires == 0
    cov_nf = paired(cov_correct[nf], maj_correct[nf])
    cov_nf_twin = paired(cov_correct[nf], twin_correct[nf])
    return {
        "n": n, "coverage_typepair": float(covered.mean()), "fd_fire_rate": float(fd_fires.mean()),
        "acc": {"covariation": float(cov_correct.mean()), "force_dynamic": float(fd_correct.mean()),
                "majority": float(maj_correct.mean()), "cov_twin": float(twin_correct.mean())},
        "covariation_minus_majority": paired(cov_correct, maj_correct),
        "covariation_minus_twin": paired(cov_correct, twin_correct),
        "covariation_minus_forcedynamic": paired(cov_correct, fd_correct),
        "on_no_fire_subset": {"n": int(nf.sum()),
                              "covariation_minus_majority": cov_nf,
                              "covariation_minus_twin": cov_nf_twin,
                              "cov_acc": float(cov_correct[nf].mean()),
                              "maj_acc": float(maj_correct[nf].mean())},
    }


def run(n_boot=2000):
    t0 = time.perf_counter()
    lex = build_force_lexicon()
    tr = load_typed_relations(TRAIN)
    va = load_typed_relations(VALID)
    model, majority = learn_typepair_model(tr)
    gen = np.random.default_rng(20260830)
    res = evaluate(va, model, majority, lex, gen, n_boot)
    res["n_train"] = len(tr)
    res["n_typepairs_learned"] = len(model)
    # the decisive contrast: covariation carries signal (beats its twin) where force-dynamics did not (RERUN 2 +0.018 NOT_SEP)
    cmt = res["covariation_minus_twin"]
    res["VERDICT"] = ("IMPLICIT_COVARIATION_IS_THE_MISSING_SIGNAL"
                      if cmt["band"] == "ABOVE" else "COVARIATION_ALSO_FLAT")
    res["meta"] = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0}
    _log("valid causal n=%d | learned %d type-pairs from %d train | type-pair coverage=%.3f"
         % (res["n"], len(model), len(tr), res["coverage_typepair"]))
    _log("acc: COVARIATION=%.3f  force_dynamic=%.3f  majority=%.3f  cov_twin=%.3f"
         % (res["acc"]["covariation"], res["acc"]["force_dynamic"], res["acc"]["majority"], res["acc"]["cov_twin"]))
    _log("covariation - majority = %+.3f %s | covariation - twin = %+.3f %s | covariation - force_dynamic = %+.3f %s"
         % (res["covariation_minus_majority"]["delta"], res["covariation_minus_majority"]["band"],
            cmt["delta"], cmt["band"],
            res["covariation_minus_forcedynamic"]["delta"], res["covariation_minus_forcedynamic"]["band"]))
    nf = res["on_no_fire_subset"]
    _log("on the 83.9%% NO-FIRE subset (n=%d): covariation=%.3f vs majority=%.3f (cov-maj %+.3f %s | cov-twin %+.3f %s)"
         % (nf["n"], nf["cov_acc"], nf["maj_acc"], nf["covariation_minus_majority"]["delta"],
            nf["covariation_minus_majority"]["band"], nf["covariation_minus_twin"]["delta"],
            nf["covariation_minus_twin"]["band"]))
    _log("VERDICT = %s" % res["VERDICT"])
    return res


def self_test():
    _log("SELF-TEST: MAVEN train+valid load; type-pair model learns; covariation vs force-dynamic differ")
    lex = build_force_lexicon()
    tr = load_typed_relations(TRAIN)
    va = load_typed_relations(VALID)
    assert len(tr) > 20000 and len(va) > 5000, "unexpected sizes tr=%d va=%d" % (len(tr), len(va))
    model, majority = learn_typepair_model(tr)
    assert len(model) > 500, "too few type-pairs learned: %d" % len(model)
    assert majority in ("CAUSE", "ENABLE")
    _log("  train=%d valid=%d typepairs=%d majority=%s" % (len(tr), len(va), len(model), majority))
    _log("SELF-TEST PASS")
    return {"n_train": len(tr), "n_valid": len(va), "typepairs": len(model)}


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
