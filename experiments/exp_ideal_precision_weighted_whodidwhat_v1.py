"""exp_ideal_precision_weighted_whodidwhat_v1 -- PROTOTYPE of the ideal register-robust who-did-what FRONT-END:
precision-weighted (reliability-weighted) constraint-satisfaction cue integration, the brain's IDEAL-ADAPTER
mechanism (Kleinschmidt & Jaeger 2015; Ernst & Banks 2002 precision weighting; MacDonald 1994 constraint-based
lexicalist), driven by CALIBRATED confidence.

WHY THIS IS THE IDEAL (from the measured ladder + the research drill):
- The register gap is NOT verb detection (the calibrated CRF tagger matches the brain) and NOT a parser-capacity /
  word-order retraining problem. The reach-stage gap is dominated by a copula-convention MEASUREMENT artifact (register
  -native REFUTED that lever) plus a modest open-verb parse gap; the real residual is SELECTION.
- The brain does NOT retrain its parser for 19c. It re-weights a MIXTURE of cues it already has (position, parse,
  selectional) by their RELIABILITY, deferring to register-robust cues (position/morphology) when the modern-trained
  parser is uncertain. Precision weighting REQUIRES CALIBRATED confidence -- which the perceptron's saturated posterior
  cannot provide and this problem's calibrated tagger/parser CAN. That is the keystone tie to the upstream fix.

THE PROTOTYPE: who-did-what argument selection on 19c (LB pop) by combining, per candidate,
  parse cue    = does it reach the verb through the arc-eager parse (register-brittle; reliable when the parser is
                 CONFIDENT), and
  position cue = English canonical structural prior (post-verbal object-ward; register-INVARIANT; Bates & MacWhinney
                 Competition Model -- position dominates in English),
weighted by the parse's CALIBRATED per-sentence confidence (arc-eager softmax attach conf). When the parser is
confident, trust structure; when not (common on 19c OOD word-order), defer to the register-robust position cue.

ARMS: BASE (parse-only chain_pick, the live pipeline) | POSITION (position-only) | IDEAL (precision-weighted, calibrated
conf) | TWIN (IDEAL with SHUFFLED conf -- info-free reliability) | UNCALIB (IDEAL with a CONSTANT conf = corpus mean --
removes the per-sentence calibration signal, the keystone ablation). PASS = IDEAL beats BASE CI-sep AND beats TWIN AND
UNCALIB CI-sep (per-sentence CALIBRATED confidence is what makes precision-weighting work).

Glass-box, CPU, NO LLM. ASCII. own dir.
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
# KB_REFERENT: data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_register_predicate_detector_v1 as D
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_arceager_parser_operator_v1 as AEO
import experiments.exp_register_native_pp_attachment_v1 as PP
from hdlab.predicate_argument_frontend import _attaches_to_verb

OUT_DIR = os.path.join(_REPO, "data/exp_ideal_precision_weighted_whodidwhat_v1")
MAX_HOPS = PP.MAX_HOPS
NOMINAL = ("NOUN", "PROPN", "PRON")


def position_prior(c, vi, n):
    """Register-INVARIANT English canonical structural prior over a candidate token index c given the verb at vi.
    Post-verbal (object-ward) preferred, decaying with distance; pre-verbal (subject-ward) weaker (Bates & MacWhinney)."""
    if c > vi:
        return 1.0 / (1.0 + (c - vi))
    return 0.4 / (1.0 + (vi - c))


def paired_boot(a, b, n_boot=2000, seed=20260903):
    a = np.asarray(a, float); b = np.asarray(b, float)
    rng = np.random.default_rng(seed); n = len(a); d = a - b
    rr = np.array([d[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    lo, hi = float(np.percentile(rr, 2.5)), float(np.percentile(rr, 97.5))
    return {"delta": round(float(d.mean()), 4), "ci": [round(lo, 4), round(hi, 4)],
            "half": round((hi - lo) / 2, 4), "sep": bool(lo > 0), "a": round(float(a.mean()), 4), "b": round(float(b.mean()), 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--cap", type=int, default=4000)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    cap = 400 if args.self_test else args.cap

    tg = D.tagger(); W_lex = AEO.load_model(AEO.MODEL_PATH)
    rows = [r for r in V1.load_pop(D.LB)[:cap] if PP.cand_ok(r)]

    # First pass: collect per-record cue data + the corpus mean confidence (for the UNCALIB constant).
    recs = []
    confs = []
    for r in rows:
        toks = r["sent"].split(); vi = r["verb_idx"]; gi = r.get("gold_idx")
        if not toks or gi is None or not (0 <= vi < len(toks)):
            continue
        cand = [c for c in r["cand_idx"] if 0 <= c < len(toks)]
        if len(cand) < 2:
            continue
        pos = tg.tag(toks)
        heads, conf, marg = AEO.parse_with_conf(toks, pos, W_lex)
        conf_sent = float(np.mean([conf.get(i + 1, 0.0) for i in range(len(toks))])) if toks else 0.0
        confs.append(conf_sent)
        reach = {c: int(_attaches_to_verb(c + 1, vi + 1, heads, pos, max_hops=MAX_HOPS)) for c in cand}
        ppri = {c: position_prior(c, vi, len(toks)) for c in cand}
        recs.append({"toks": toks, "vi": vi, "gold_head": r["gold_head"], "cand": cand,
                     "reach": reach, "ppri": ppri, "conf": conf_sent, "r": r, "pos": pos, "heads": heads})
    conf_const = float(np.mean(confs)) if confs else 0.5

    rng = np.random.default_rng(7)
    shuffled = list(range(len(recs))); rng.shuffle(shuffled)

    def pick_base(e):
        return PP.chain_pick(e["r"], e["toks"], e["pos"], e["heads"], "far")

    def pick_position(e):
        c = max(e["cand"], key=lambda c: e["ppri"][c])
        return e["toks"][c]

    def pick_weighted(e, w):
        # precision-weighted: score(c) = w*reach(c) + (1-w)*normalized_position_prior(c)
        pmax = max(e["ppri"].values()) or 1.0
        best = None; bs = -1e9
        for c in e["cand"]:
            s = w * e["reach"][c] + (1.0 - w) * (e["ppri"][c] / pmax)
            if s > bs:
                bs = s; best = c
        return e["toks"][best]

    ok = {k: [] for k in ("base", "position", "ideal", "twin", "uncalib")}
    for i, e in enumerate(recs):
        g = e["gold_head"]
        ok["base"].append(int(pick_base(e) == g))
        ok["position"].append(int(pick_position(e) == g))
        ok["ideal"].append(int(pick_weighted(e, e["conf"]) == g))                     # calibrated per-sentence conf
        ok["twin"].append(int(pick_weighted(e, recs[shuffled[i]]["conf"]) == g))       # info-free shuffled conf
        ok["uncalib"].append(int(pick_weighted(e, conf_const) == g))                   # constant conf (no per-sent calib)

    res = {"n": len(recs), "conf_const": round(conf_const, 4),
           "acc": {k: round(float(np.mean(v)), 4) for k, v in ok.items()},
           "ideal_vs_base": paired_boot(ok["ideal"], ok["base"]),
           "ideal_vs_position": paired_boot(ok["ideal"], ok["position"]),
           "ideal_vs_twin": paired_boot(ok["ideal"], ok["twin"]),
           "ideal_vs_uncalib": paired_boot(ok["ideal"], ok["uncalib"]),
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "ideal_precision_weighted_whodidwhat_v1", "results": res}, f, indent=2)

    print("\n===== IDEAL precision-weighted who-did-what (n=%d, 19c LB) =====" % res["n"], flush=True)
    for k in ("base", "position", "ideal", "twin", "uncalib"):
        print("  %-9s acc=%.4f" % (k, res["acc"][k]), flush=True)
    for nm, key in (("ideal - base    ", "ideal_vs_base"), ("ideal - position", "ideal_vs_position"),
                    ("ideal - twin    ", "ideal_vs_twin"), ("ideal - uncalib ", "ideal_vs_uncalib")):
        d = res[key]
        print("  %s = %+.4f CI%s sep=%s" % (nm, d["delta"], d["ci"], d["sep"]), flush=True)
    if args.self_test:
        assert res["n"] > 0
        print("[self-test] PASS", flush=True)
    print("[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
