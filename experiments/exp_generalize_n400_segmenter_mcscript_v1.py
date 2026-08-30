"""exp_generalize_n400_segmenter_mcscript_v1 -- GENERALIZATION rerun of the N400 prediction-error EVENT
SEGMENTER on a real pre-existing corpus (MCScript2, Ostermann et al. 2019).

ORGAN: the_substrate_does_not_learn_or_update_by_prediction_error. Headline: a GRADED forward content
prediction-error (N400 = novelty of the current content vs the running event-gist) segments discourse into
events -- downstream cross-role recovery 0.9881 on SYNTHETIC K=8 clean-topic-jump streams (boundary F1
0.987), vs FORM_NOVELTY 0.7367 / FIXED_k 0.5225 / RANDOM 0.4375, twin PERMUTED_SURPRISE p95 ~0.51. The
solver flagged real-text segmentation as the unbuilt next step.

THE POPULATION (the classic Choi document-concatenation segmentation setup, = the "near-orthogonal topic
jump" the synthetic mimics, but with REAL prose): each MCScript2 <instance> is ONE coherent scenario
narrative (renovating a room / drying clothes / ...). Concatenate several scenarios in random order at the
SENTENCE level; the seam between two scenarios is a GOLD event boundary. n = hundreds of boundaries over
many streams.

THE MECHANISM (imported VERBATIM from the landed organ): hdlab.predictive_coding.relative_threshold_gate
(EST self-referential boundary detector, Reynolds/Zacks/Braver 2007) + running_avg_update. Content vector =
glass-box TF over content lemmas (the distributional-content analog); running event-gist = mean of sentences
since the last fired boundary (resets at a boundary); content-PE = residual_magnitude(sentence, gist) =
(1-cos)/2; boundary fires when content-PE / its own running baseline >= threshold.

ARMS: N400_content (the organ) vs FORM_NOVELTY (surface new-word rate, no semantic gist), FIXED_k (boundary
every k = mean scenario length), RANDOM_ratematched. Info-free twin = PERMUTED_SURPRISE (the N400 PE
sequence shuffled across positions -> same magnitudes, wrong places). Threshold calibrated on VAL streams to
match the true boundary RATE (event-length prior), NEVER the metric. Metric = boundary-detection F1 (+-1
sentence tolerance, standard for segmentation). Bootstrap CI over streams. NO external LLM. CPU. ASCII-only.
Deterministic.

Run: .venv/Scripts/python.exe experiments/exp_generalize_n400_segmenter_mcscript_v1.py --self-test
     ... --full
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.predictive_coding import relative_threshold_gate, running_avg_update, residual_magnitude  # noqa: E402

ANCHOR = "generalize_n400_segmenter_mcscript_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
MCS = os.path.join(REPO, "data", "corpora", "mcscript2", "extracted", "dev-data.xml")

STOP = set("the a an and or but if then of to in on at for with from by as is are was were be been being "
           "it its this that these those i we you he she they them his her our your my me him us their "
           "so we us do did done have has had will would can could should may might must not no yes there "
           "here what when where who why how which while about into out up down over under again very "
           "just more most some any all each other one two first next after before then had s t".split())


def _tokens(text):
    return [w for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 3 and w not in STOP]


def load_scenarios(path):
    """Each instance -> (scenario_label, [sentence_token_lists])."""
    root = ET.parse(path).getroot()
    out = []
    for inst in root:
        te = inst.find("text")
        if te is None or not (te.text or "").strip():
            continue
        # mcscript2 uses spaced punctuation; split on sentence-final ' . '/'? '/'! '
        sents = re.split(r"\s+[.?!]\s+", te.text.strip())
        toks = [_tokens(s) for s in sents]
        toks = [t for t in toks if len(t) >= 2]  # keep contentful sentences
        if len(toks) >= 3:
            out.append((inst.attrib.get("scenario", "?"), toks))
    return out


def build_stream(scenarios, idxs):
    """Concatenate the chosen scenarios; return (list_of_sentence_tokenlists, gold_boundary_positions)."""
    sents, gold = [], set()
    for j, si in enumerate(idxs):
        _lab, toks = scenarios[si]
        if j > 0:
            gold.add(len(sents))   # the seam: first sentence of a new scenario
        sents.extend(toks)
    return sents, gold


def _vec(tok_list, vocab):
    v = np.zeros(len(vocab), dtype=np.float64)
    for w in tok_list:
        k = vocab.get(w)
        if k is not None:
            v[k] += 1.0
    return v


def n400_boundaries(sents, vocab, threshold, decay=0.05):
    """The organ: content-PE vs a running event-gist (resets at boundaries) + relative_threshold_gate.
    Returns (boundary_positions_set, pe_sequence)."""
    gist = None
    gist_n = 0
    pe_base = None
    bounds, pes = set(), []
    for i, toks in enumerate(sents):
        svec = _vec(toks, vocab)
        if gist is None:
            gist, gist_n = svec.copy(), 1
            pes.append(0.0)
            continue
        pe = residual_magnitude(svec, gist)
        pes.append(pe)
        dec = relative_threshold_gate(svec, gist, running_avg_prev=pe_base, threshold=threshold)
        if dec.is_boundary:
            bounds.add(i)
            gist, gist_n = svec.copy(), 1
        else:
            gist = (gist * gist_n + svec) / (gist_n + 1); gist_n += 1
        pe_base = running_avg_update(pe_base, pe, decay=decay)
    return bounds, pes


def form_novelty_boundaries(sents, threshold, decay=0.05):
    """FLOOR: surface new-word rate vs the accumulated event word-set (no semantic gist). Same relative gate."""
    seen = set()
    pe_base = None
    bounds = []
    bset = set()
    for i, toks in enumerate(sents):
        if not seen:
            seen = set(toks)
            continue
        new = sum(1 for w in toks if w not in seen)
        pe = new / max(1, len(toks))
        if pe_base is not None and pe_base > 1e-9 and (pe / pe_base) >= threshold:
            bset.add(i); seen = set(toks)
        else:
            seen |= set(toks)
        pe_base = running_avg_update(pe_base, pe, decay=decay)
    return bset


def fixed_k_boundaries(n, k):
    return set(range(k, n, max(1, k)))


def random_boundaries(n, rate, gen):
    return set(int(i) for i in range(1, n) if gen.random() < rate)


def permuted_surprise_boundaries(pes, threshold, gen, decay=0.05):
    """TWIN: the N400 PE magnitudes shuffled across positions, same relative gate -> right rate, wrong places."""
    idx = gen.permutation(len(pes))
    shuf = np.array(pes)[idx]
    pe_base = None
    bset = set()
    for i, pe in enumerate(shuf):
        if pe_base is not None and pe_base > 1e-9 and (pe / pe_base) >= threshold:
            bset.add(i)
        pe_base = running_avg_update(pe_base, float(pe), decay=decay)
    return bset


def f1(pred, gold, n, tol=1):
    """Boundary-detection F1 with +-tol sentence tolerance."""
    if not gold:
        return None
    tp = sum(1 for g in gold if any(abs(g - p) <= tol for p in pred))
    fp = sum(1 for p in pred if not any(abs(g - p) <= tol for g in gold))
    fn = len(gold) - tp
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    return (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0


def make_streams(scenarios, n_streams, k_scenarios, gen):
    streams = []
    for _ in range(n_streams):
        idxs = gen.choice(len(scenarios), size=k_scenarios, replace=False)
        streams.append(build_stream(scenarios, [int(i) for i in idxs]))
    return streams


def calibrate_threshold(streams, mode, true_rate, gen):
    """Pick the relative threshold whose realized boundary rate is closest to the true seam rate
    (the event-length prior) -- calibrated on VAL streams, never on F1."""
    best, best_gap = 2.0, 1e9
    for T in [1.2, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 3.5, 4.0]:
        rates = []
        for sents, _gold in streams:
            vocab = {w: i for i, w in enumerate(sorted({w for s in sents for w in s}))}
            if mode == "n400":
                b, _ = n400_boundaries(sents, vocab, T)
            else:
                b = form_novelty_boundaries(sents, T)
            rates.append(len(b) / max(1, len(sents)))
        gap = abs(float(np.mean(rates)) - true_rate)
        if gap < best_gap:
            best_gap, best = gap, T
    return best


def evaluate(streams, T_n400, T_form, gen, n_boot=2000):
    per = {a: [] for a in ["N400_content", "FORM_NOVELTY", "FIXED_k", "RANDOM", "TWIN"]}
    all_sent_lens = [len(s) for s, _ in streams]
    k = max(2, int(round(np.mean([len(s) / (len(g) + 1) for s, g in streams]))))  # mean scenario length
    true_rate = float(np.mean([len(g) / max(1, len(s)) for s, g in streams]))
    for sents, gold in streams:
        n = len(sents)
        vocab = {w: i for i, w in enumerate(sorted({w for s in sents for w in s}))}
        nb, pes = n400_boundaries(sents, vocab, T_n400)
        per["N400_content"].append(f1(nb, gold, n))
        per["FORM_NOVELTY"].append(f1(form_novelty_boundaries(sents, T_form), gold, n))
        per["FIXED_k"].append(f1(fixed_k_boundaries(n, k), gold, n))
        per["RANDOM"].append(f1(random_boundaries(n, true_rate, gen), gold, n))
        per["TWIN"].append(f1(permuted_surprise_boundaries(pes, T_n400, gen), gold, n))
    per = {a: [x for x in v if x is not None] for a, v in per.items()}

    def ci(vals):
        vals = np.array(vals, dtype=np.float64)
        b = np.array([gen.choice(vals, size=len(vals), replace=True).mean() for _ in range(n_boot)])
        return {"mean": float(vals.mean()), "lo": float(np.percentile(b, 2.5)), "hi": float(np.percentile(b, 97.5))}

    def paired(a, b):
        a, b = np.array(per[a]), np.array(per[b])
        d = a - b
        idx = np.array([gen.integers(0, len(d), size=len(d)) for _ in range(n_boot)])
        bt = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))
        null = np.array([np.abs((d * gen.choice([-1.0, 1.0], size=len(d))).mean()) for _ in range(n_boot)])
        p95 = float(np.percentile(null, 95))
        band = "ABOVE" if lo > 0 and lo > p95 else ("BELOW" if hi < 0 else "NOT_SEP")
        return {"delta": float(d.mean()), "lo": lo, "hi": hi, "null_p95": p95, "band": band}

    means = {a: ci(v) for a, v in per.items()}
    contrasts = {"n400_minus_form": paired("N400_content", "FORM_NOVELTY"),
                 "n400_minus_fixed": paired("N400_content", "FIXED_k"),
                 "n400_minus_random": paired("N400_content", "RANDOM"),
                 "n400_minus_twin": paired("N400_content", "TWIN")}
    return {"means": means, "contrasts": contrasts, "k_fixed": k, "true_boundary_rate": true_rate,
            "n_streams": len(streams)}


def run(mode="full", n_boot=2000):
    t0 = time.perf_counter()
    scen = load_scenarios(MCS)
    gen = np.random.default_rng(20260830)
    n_streams = 120 if mode == "full" else 20
    k_scen = 5
    # split scenarios into VAL / TEST halves so calibration never sees the test streams
    perm = gen.permutation(len(scen))
    val_scen = [scen[i] for i in perm[: len(scen) // 2]]
    test_scen = [scen[i] for i in perm[len(scen) // 2:]]
    val_streams = make_streams(val_scen, 40 if mode == "full" else 10, k_scen, gen)
    test_streams = make_streams(test_scen, n_streams, k_scen, gen)
    true_rate = float(np.mean([len(g) / max(1, len(s)) for s, g in val_streams]))
    T_n400 = calibrate_threshold(val_streams, "n400", true_rate, gen)
    T_form = calibrate_threshold(val_streams, "form", true_rate, gen)
    res = evaluate(test_streams, T_n400, T_form, gen, n_boot)
    res["thresholds"] = {"n400": T_n400, "form_novelty": T_form, "calibrated_rate": true_rate}
    res["n_scenarios"] = len(scen)
    c = res["contrasts"]
    res["VERDICT"] = ("HOLDS" if all(c[k]["band"] == "ABOVE" for k in
                                     ["n400_minus_form", "n400_minus_fixed", "n400_minus_random", "n400_minus_twin"])
                      else "DOES_NOT_HOLD")
    res["meta"] = {"anchor": ANCHOR, "ts_iso": _now(), "elapsed_s": time.perf_counter() - t0}
    m = res["means"]
    _log("scenarios=%d streams=%d k_fixed=%d rate=%.3f | thr n400=%.2f form=%.2f"
         % (len(scen), res["n_streams"], res["k_fixed"], res["true_boundary_rate"], T_n400, T_form))
    _log("boundary-F1: N400=%.3f[%.3f,%.3f]  FORM=%.3f  FIXED_k=%.3f  RANDOM=%.3f  TWIN=%.3f"
         % (m["N400_content"]["mean"], m["N400_content"]["lo"], m["N400_content"]["hi"],
            m["FORM_NOVELTY"]["mean"], m["FIXED_k"]["mean"], m["RANDOM"]["mean"], m["TWIN"]["mean"]))
    for k in ["n400_minus_form", "n400_minus_fixed", "n400_minus_random", "n400_minus_twin"]:
        _log("  %s = %+.3f [%.3f,%.3f] %s" % (k, c[k]["delta"], c[k]["lo"], c[k]["hi"], c[k]["band"]))
    _log("VERDICT = %s" % res["VERDICT"])
    return res


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def self_test():
    _log("SELF-TEST: mcscript2 loads; streams have gold seams; landed gate imported")
    scen = load_scenarios(MCS)
    assert len(scen) > 100, "too few scenarios: %d" % len(scen)
    gen = np.random.default_rng(1)
    sents, gold = build_stream(scen, [0, 1, 2])
    assert len(gold) == 2, "3 scenarios -> 2 seams, got %d" % len(gold)
    assert all(0 < g < len(sents) for g in gold)
    _log("  scenarios=%d | sample stream len=%d seams=%s" % (len(scen), len(sents), sorted(gold)))
    _log("SELF-TEST: F1 tolerance + a perfect predictor scores 1.0")
    assert f1(gold, gold, len(sents)) == 1.0, "perfect prediction must be F1=1.0"
    assert abs(f1(set(), gold, len(sents)) - 0.0) < 1e-9, "empty prediction F1=0"
    _log("SELF-TEST PASS")
    return {"n_scenarios": len(scen)}


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
                      {"verdict": "SELFTEST_PASS", "selftest": st, "ts_iso": _now()})
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return
    res = run("full")
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), res)
    _log("DONE full in %.1fs -> %s" % (time.perf_counter() - t0, OUTPUT_DIR))


if __name__ == "__main__":
    main()
