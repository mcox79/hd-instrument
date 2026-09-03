"""exp_register_predicate_ideal_v1 -- the IDEAL, exactly-brain-foundational predicate detector, prototyped as an
ablation ladder where each rung fixes one MEASURED mechanism-difference from the brain (SS4b of SOLVED.md).

The mechanism diffs and their brain-faithful fixes:
  (ii) brain CONTINUOUSLY re-estimates category from context; we froze the Viterbi-ARGMAX emission margin.
       FIX = the FORWARD-BACKWARD MARGINAL posterior P(VERB | WHOLE sentence) over the tagger's OWN potentials -- a
       graded, context-integrated category belief (Lee-Federmeier 2009 dominant-reading-stays-active; MacDonald 1994
       graded settling), NOT a committed argmax. This is the single biggest, cleanest fix, targeting the 19c FIDELITY
       gap (competent reader recovers ~1.0; our frozen-margin detector 0.56).
  (i)  brain settles category+structure JOINTLY; we tag-then-patch. FIX = joint parse-coherence (global_delta: does
       forcing VERB improve the whole-sentence parse). --with-parse.
  (iv) brain has a TOP-DOWN semantic/discourse prior for the hardest cases; we have none. This is the ~33%-of-modern
       genuine ceiling and needs the MEANING HUB (north-star P1, largely unbuilt) -- documented as the seam, not faked
       with a register-brittle thematic-fit cue (the register-native problem REFUTED that on 19c).

ARMS (isolate each fix; recovery @ FP<=0.5, modern-CV + 19c-transfer, info-free twin):
  R0 FROZEN   = the landed v1 detector (emission-argmax margin)         -- baseline
  R1 MARGINAL = replace the frozen margin with the forward-backward posterior   -- fix (ii)
  R2 +PARSE   = R1 + joint parse-coherence global_delta                 -- fix (i)   [--with-parse]
HEADLINE: does the MARGINAL posterior (context re-estimation) close the 19c fidelity gap the frozen margin leaves?

Glass-box, CPU, NO LLM/spaCy. ASCII. own dir.
# KB_REFERENT: data/frontend_assets/pos_tagger_ud_ewt_upos.json
# KB_REFERENT: data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
# KB_REFERENT: data/benchmark_trap_check/qasrl/qasrl-v2/orig/dev.jsonl.gz
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

from hdlab.pos_tagger import pos_features, pos_transition
import experiments.exp_register_predicate_detector_v1 as D
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_whodidwhat_verb_id_recoverable_v1 as VID

OUT_DIR = os.path.join(_REPO, "data/exp_register_predicate_ideal_v1")


def forward_backward_verb_posterior(toks, W, tags):
    """Marginal P(tag_i = VERB | whole sentence) under the perceptron's implied Gibbs distribution p(y) ~ exp(score(y)).
    Log-space forward-backward over the tagger's OWN emission+transition potentials. Context-INTEGRATED (unlike the
    local argmax emission margin) -> the graded, continuously-re-estimated category belief the brain uses."""
    n = len(toks); K = len(tags)
    if n == 0:
        return []
    em = np.array([[sum(W.get(f, 0.0) for f in pos_features(toks, i, tags[k])) for k in range(K)] for i in range(n)])
    TM = np.array([[W.get(pos_transition(tags[j], tags[k]), 0.0) for k in range(K)] for j in range(K)])
    SV = np.array([W.get(pos_transition("<S>", tags[k]), 0.0) for k in range(K)])

    def lse(a, axis=None):
        m = np.max(a, axis=axis, keepdims=True)
        return (m + np.log(np.sum(np.exp(a - m), axis=axis, keepdims=True))).squeeze(axis)

    la = np.empty((n, K)); la[0] = em[0] + SV
    for i in range(1, n):
        la[i] = em[i] + lse(la[i - 1][:, None] + TM, axis=0)
    lb = np.zeros((n, K))
    for i in range(n - 2, -1, -1):
        lb[i] = lse(TM + (em[i + 1] + lb[i + 1])[None, :], axis=1)
    Z = lse(la[n - 1], axis=0)
    vi = tags.index("VERB") if "VERB" in tags else 0
    post = np.exp((la + lb - Z)[:, vi])
    return post.tolist()


def _logit(p):
    p = min(max(float(p), 1e-6), 1 - 1e-6)
    return float(np.log(p / (1 - p)))


def feats_arm(toks, pos, i, W, tags, post, arm, Wp, parse_fn):
    """Shared structural cues + the arm-specific CATEGORY-EVIDENCE feature. The marginal posterior is fed in LOG-ODDS
    (logit) space -- its natural scale, = the context-integrated log-likelihood-ratio (the noisy-channel quantity);
    the raw posterior is saturated near 0 and mis-scales a standardized logistic."""
    base = D.feats_parsefree(toks, pos, i, W, tags)   # [verb_margin, frame, subj, obj, morph, verbless, relpos]
    frozen_margin = base[0]; rest = base[1:]
    lp = _logit(post[i])
    if arm == "R0_FROZEN":
        cat = [frozen_margin]
    elif arm == "R3_BOTH":                             # local margin + context-integrated posterior (the ideal)
        cat = [frozen_margin, lp]
    else:                                              # R1_MARGINAL / R2_PARSE: context-integrated posterior (fix ii)
        cat = [lp]
    fv = cat + rest
    if arm == "R2_PARSE":
        fv = fv + D.parse_signals(toks, pos, i, Wp, parse_fn)  # global structural coherence (fix i)
    return fv


def build_rows(sents, W, tags, arm, Wp, parse_fn):
    tg = D.tagger(); rows = []; nsent = 0
    for toks, gold_verb in sents:
        if not toks:
            continue
        pos = tg.tag(toks)
        post = forward_backward_verb_posterior(toks, W, tags)
        dropped = set(i for i in gold_verb if pos[i] not in ("VERB", "AUX"))
        for i in range(len(toks)):
            if pos[i] in ("VERB", "AUX") or not VID.has_verb_reading(toks[i]):
                continue
            rows.append((nsent, i, feats_arm(toks, pos, i, W, tags, post, arm, Wp, parse_fn), 1 if i in dropped else 0))
        nsent += 1
    return rows, nsent


def build_rows_19c(pop, W, tags, arm, Wp, parse_fn, cap=None):
    tg = D.tagger(); rows = []; nsent = 0
    pop = pop[:cap] if cap else pop
    for r in pop:
        toks = r["sent"].split(); vi = r["verb_idx"]
        if not toks or vi >= len(toks):
            continue
        pos = tg.tag(toks)
        post = forward_backward_verb_posterior(toks, W, tags)
        gv = {vi} if (pos[vi] not in ("VERB", "AUX")) else set()
        for i in range(len(toks)):
            if pos[i] in ("VERB", "AUX") or not VID.has_verb_reading(toks[i]):
                continue
            rows.append((nsent, i, feats_arm(toks, pos, i, W, tags, post, arm, Wp, parse_fn), 1 if i in gv else 0))
        nsent += 1
    return rows, nsent


def run_arm(arm, ud, qasrl, pop, W, tags, Wp, parse_fn, lbcap):
    mod_rows, mod_ns = build_rows(ud, W, tags, arm, Wp, parse_fn)
    q_rows, _ = build_rows(qasrl, W, tags, arm, Wp, parse_fn)
    modern = D.evaluate(mod_rows, mod_ns, D.cv_proba(mod_rows))
    clf, mu, sd = D._fit(mod_rows + q_rows)
    c19_rows, c19_ns = build_rows_19c(pop, W, tags, arm, Wp, parse_fn, cap=lbcap)
    c19 = D.evaluate(c19_rows, c19_ns, D._proba(clf, mu, sd, c19_rows))
    def pack(r):
        b = r["best_fp_le_0p5"]; bt = r["bootstrap_delta_vs_twin"]
        return {"recovery@0.5FP": b["recovery"] if b else None, "fp": b["false_verbs_per_sent"] if b else None,
                "delta_vs_twin": bt["delta_vs_twin_mean"] if bt else None,
                "ci": bt["ci"] if bt else None, "sep": (bt["ci"][0] > 0) if bt else None,
                "n_pos": r["n_positives"]}
    return {"modern": pack(modern), "c19_transfer": pack(c19)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--with-parse", action="store_true", dest="with_parse")
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tg = D.tagger(); W = tg._perc.weights; tags = tg.tags
    Wp = None; parse_fn = None
    if args.with_parse:
        from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
        Wp = load_model(MODEL_PATH); parse_fn = parse_with_conf

    cap = 60 if args.self_test else (150 if args.smoke else (None if args.full else 700))
    qcap = 60 if args.self_test else (150 if args.smoke else (1500 if args.full else 1200))  # QA is training-enrichment; cap even in full (forward-backward cost)
    lbcap = 400 if (args.self_test or args.smoke) else (None if args.full else 2500)

    ud = D.load_ud(D.UD_TEST, cap=cap)
    qasrl = D.load_qasrl(D.QASRL, cap=qcap)
    pop = V1.load_pop(D.LB)

    arms = ["R0_FROZEN", "R1_MARGINAL", "R3_BOTH"] + (["R2_PARSE"] if args.with_parse else [])
    results = {}
    for arm in arms:
        print("running %s ..." % arm, flush=True)
        results[arm] = run_arm(arm, ud, qasrl, pop, W, tags, Wp, parse_fn, lbcap)

    # headline: does the marginal (R1) close the 19c fidelity gap vs frozen (R0)?
    r0 = results["R0_FROZEN"]["c19_transfer"]["recovery@0.5FP"]
    r1 = results["R1_MARGINAL"]["c19_transfer"]["recovery@0.5FP"]
    res = {"arms": results, "c19_gap_closed_marginal_minus_frozen": round((r1 or 0) - (r0 or 0), 4),
           "competent_reader_19c_ceiling": 1.0,
           "diff_iv_semantic_seam": "the ~33%-of-modern genuine ceiling needs the MEANING HUB (P1, largely unbuilt); "
                                    "not faked here with a register-brittle thematic-fit cue (register-native REFUTED it on 19c)."}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "register_predicate_ideal_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)

    print("\n===== IDEAL (brain-foundational) ablation ladder -- recovery @ FP<=0.5 =====", flush=True)
    print("  %-14s %18s %18s" % ("arm", "MODERN", "19c-TRANSFER"), flush=True)
    for arm in arms:
        m = results[arm]["modern"]; c = results[arm]["c19_transfer"]
        print("  %-14s  rec=%.4f sep=%-5s  rec=%.4f sep=%-5s" % (
            arm, m["recovery@0.5FP"] or 0, m["sep"], c["recovery@0.5FP"] or 0, c["sep"]), flush=True)
    print("\n  19c gap closed by the MARGINAL posterior (R1-R0): %+.4f   (competent-reader ceiling = 1.0)" % res["c19_gap_closed_marginal_minus_frozen"], flush=True)

    if args.self_test or args.smoke:
        assert "R1_MARGINAL" in results
        print("\n[self-test] PASS", flush=True)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
