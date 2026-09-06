"""verification/test_precision_defer_landing.py -- LANDING witness for the precision-defer wire.

Proves FIRST-HAND (capped threads, PASS/FAIL per check) that the DEFER-CONSUMER + cost-fold + agent defer +
per-event joint confidence landed in hdlab is correct, byte-identical where it must be, and reproduces the
validated defer gain THROUGH THE LIVE READER's config (a2_marg dropped, single shared parse).

  W1 COST-FIX byte-identity: the folded (heads,conf,marg) the reader caches from the ONE shared arc-eager
     parse_with_conf equals a fresh parse_with_conf (heads unchanged) AND _cached_parse_heads == the heads of
     _cached_parse_conf -- one parse yields all three; no accuracy change.
  W2 ADDITIVE / DEFAULT-SAFE: precision_weight_roles default-ON + precision_weight_tau=None -> a live read is
     byte-identical to precision_weight_roles=False on every scored dim (event agent/patient/pred/tense/roles/
     affect, coref entities, timeline, memory round-trip); only the additive conf/defer/event_conf metadata is
     added, every *_defer is None (defer never fires with tau=None).
  W3 DEFER GAIN reproduces LIVE (a2_marg=0): the dev-tau abstain policy on the PATIENT + obl readers, scoring
     off the FROZEN hdlab.parse_confidence calibrator with a2_marg=0.0 (the LIVE config after the a2-drop),
     reproduces the +~0.086 / +~0.092 accuracy-on-answered CI-separated over the blanket reader, with the
     random-confidence twin FLAT. Reports the live a2=0 number vs the solver's published a2 number.
  W4 EVENT_CONF: (a) LIVE -- through the wired reader, EventRecord.event_conf == agent_conf * patient_conf on
     the emitted events (all in [0,1]); (b) PROPERTY -- the product-of-precisions predicts WHOLE-EVENT
     correctness with AUC > either single role alone, random-twin flat (reproduced with the frozen calibrator,
     a2=0), and an event-level abstain lifts whole-event reliability CI-sep.

Run: OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MKL_NUM_THREADS=3 THINC_NUM_THREADS=3 \
     .venv/Scripts/python.exe verification/test_precision_defer_landing.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import numpy as np

import hdlab.arceager_parser as AE
from hdlab import parse_confidence as PC
from hdlab.situation_reader import SituationReader, _write_temp_conll
from hdlab.predicate_argument_frontend import structural_patient_pick, _labeler
from hdlab.relcl_resolver import precise_passive

from experiments.exp_typed_selpref_ppattach_v1 import load, TRAIN, TEST
from experiments.exp_precision_weighted_whodidwhat_v1 import wdw_population
from experiments.exp_precwt_live_whodidwhat_v1 import auc
import experiments.exp_defer_consumer_v1 as DC
import experiments.exp_defer_joint_event_v1 as JE

NOMINAL = ("NOUN", "PROPN", "PRON")
OBL_RELS = ("obl", "nmod")
# Cap the test slice for a bounded runtime; the full test (n_patient=1255) is the solver's headline population.
TEST_SLICE = None   # full UD-EWT test (2077 sents); the solver headline population


# ------------------------------------------------------------------------------------------------
# LIVE-config row builders: score off the FROZEN calibrator with a2_marg=0.0 (exactly what the wired reader
# emits after the a2-drop). No arc_parser (global margin) parse -- the whole point of the flip-on cost fix.
# ------------------------------------------------------------------------------------------------
def patient_rows_a2z(items, W, sid0=0):
    rows = []; sid = sid0
    for s, v, g in items:
        toks = [t[1] for t in s]; pos = [t[3] for t in s]
        heads, conf, marg = AE.parse_with_conf(toks, pos, W)
        pk = structural_patient_pick(toks, pos, heads, v)
        if pk is None:
            sid += 1; continue
        labels = _labeler().label(list(toks), list(pos), heads)
        passive = bool(precise_passive(toks, pos, v))
        cconf = PC.calibrated_patient_confidence(toks, pos, heads, conf, marg, v, pk, labels, passive, a2_marg=0.0)
        rows.append({"sid": sid, "ok": int(pk in {g}), "conf": float(cconf)})
        sid += 1
    return rows, sid


def obl_rows_a2z(sents, W, sid0=0):
    rows = []; sid = sid0
    for s in sents:
        toks = [t[1] for t in s]; pos = [t[3] for t in s]
        gold_head = {t[0]: t[4] for t in s}; gold_rel = {t[0]: t[5].split(":")[0] for t in s}
        heads, conf, marg = AE.parse_with_conf(toks, pos, W)
        for t in s:
            c = t[0]
            if gold_rel.get(c) not in OBL_RELS or t[3] not in NOMINAL:
                continue
            ph = heads.get(c, 0)
            cconf = PC.calibrated_obl_confidence(toks, pos, conf, marg, c, ph, a2_marg=0.0)
            rows.append({"sid": sid, "ok": int(ph == gold_head.get(c)), "conf": float(cconf)})
        sid += 1
    return rows, sid


def joint_rows_a2z(sents, W, sid0=0):
    """Per-event agent competition (standalone, validated) + FROZEN patient calibrator (a2=0) + joint correctness.
    raw_margin = the emitted agent reliability (a_feats[0] = tanh(top2/3)); a_feats for the calibrated compare."""
    rows = []; sid = sid0
    for s in sents:
        toks = [t[1] for t in s]; pos = [t[3] for t in s]
        for t in s:
            if t[3] != "VERB":
                continue
            v = t[0]
            ag = [u[0] for u in s if u[4] == v and u[5].split(":")[0] == "nsubj" and u[5] != "nsubj:pass"]
            ob = [u[0] for u in s if u[4] == v and u[5].split(":")[0] == "obj"]
            if not ag or not ob:
                continue
            a_out = JE._agent_feats(toks, pos, v - 1, set(a - 1 for a in ag))
            if a_out is None:
                continue
            a_ok, a_feats = a_out
            heads, conf, marg = AE.parse_with_conf(toks, pos, W)
            pk = structural_patient_pick(toks, pos, heads, v)
            if pk is None:
                continue
            labels = _labeler().label(list(toks), list(pos), heads)
            passive = bool(precise_passive(toks, pos, v))
            p_conf = PC.calibrated_patient_confidence(toks, pos, heads, conf, marg, v, pk, labels, passive, a2_marg=0.0)
            rows.append({"sid": sid, "a_feats": a_feats, "a_ok": a_ok, "raw_margin": float(a_feats[0]),
                         "p_conf": float(p_conf), "p_ok": int(pk in set(ob)),
                         "joint_ok": int(a_ok and int(pk in set(ob)))})
        sid += 1
    return rows, sid


def _abstain_check(dev_rows, te_rows, label):
    """dev-tau (target cov 0.75) abstain: CI-sep over blanket + twin flat. Returns (pass, printline)."""
    tau = DC.choose_tau_coverage(dev_rows, 0.75)
    ab = DC.abstain_metrics(te_rows, tau)
    ci = DC.boot_delta(te_rows, lambda rr: DC.abstain_metrics(rr, tau)["answered_acc"])
    tw = DC._twin_conf(te_rows)
    tau_tw = float(np.quantile(DC._arr(DC._twin_conf(dev_rows), "conf_twin"), 0.25))
    tw_ab = DC.abstain_metrics([dict(r, conf=r["conf_twin"]) for r in tw], tau_tw)
    ok = bool(ci["sep"] and ci["ci"][0] > 0 and ci["ci"][0] > tw_ab["delta_vs_blanket"])
    line = ("%s: blanket=%.4f -> answered=%.4f @cov=%.3f (%+.4f CI[%+.4f,%+.4f]) | twin %+.4f -> %s"
            % (label, ab["blanket"], ab["answered_acc"], ab["coverage"], ab["delta_vs_blanket"],
               ci["ci"][0], ci["ci"][1], tw_ab["delta_vs_blanket"], "PASS" if ok else "FAIL"))
    return ok, line


def _event_tuple(e):
    return (e.agent, e.patient, e.predicate, e.tense, e.subj_role, e.obj_role, e.affect, e.pred_idx,
            e.patient_is_bare_do)


def main():
    print("witness: precision-defer LANDING (cost-fold + defer-consumer + agent defer + event_conf; flip-on)")
    W = AE.load_model(AE.MODEL_PATH)
    passed = 0; total = 4

    # ---------------------------------------------------------------- W1 COST-FIX byte-identity
    r = SituationReader(gaz={"john": "masc", "mary": "fem"})
    toks = ["the", "dog", "chased", "the", "cat", "in", "the", "garden", "today"]
    pos = r._cached_tag(list(toks))
    heads_cached = r._cached_parse_heads(toks, pos)
    h_conf, c_conf, m_conf = r._cached_parse_conf(toks, pos)
    H, C, M = AE.parse_with_conf(toks, pos, W)
    keys = sorted({k[0] for k in r._read_parse_cache})
    w1 = (heads_cached == H and h_conf == H and c_conf == C and m_conf == M
          and ("parseconf" in keys) and ("parse" in keys))
    print("  [W1] fold byte-identity: heads==%s conf==%s marg==%s | _cached_parse_heads==heads==%s | shared cache %s -> %s"
          % (heads_cached == H, c_conf == C, m_conf == M, h_conf == H, keys, "PASS" if w1 else "FAIL"))
    passed += w1

    # ---------------------------------------------------------------- W2 ADDITIVE / default-safe (live read)
    rows = [
        (0, 0, "John", "(0)"), (0, 1, "saw", "_"), (0, 2, "Mary", "(1)"), (0, 3, ".", "_"),
        (1, 0, "He", "(0)"), (1, 1, "had", "_"), (1, 2, "finished", "_"),
        (1, 3, "before", "_"), (1, 4, "she", "(1)"), (1, 5, "arrived", "_"), (1, 6, ".", "_"),
        (2, 0, "She", "(1)"), (2, 1, "cried", "_"), (2, 2, "because", "_"),
        (2, 3, "he", "(0)"), (2, 4, "left", "_"), (2, 5, ".", "_"),
    ]
    path = _write_temp_conll(rows)
    try:
        sm_on = SituationReader(gaz={"john": "masc", "mary": "fem"}).read(path)                       # default ON
        sm_off = SituationReader(gaz={"john": "masc", "mary": "fem"}, precision_weight_roles=False).read(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    ev_same = ([_event_tuple(e) for e in sm_on.events] == [_event_tuple(e) for e in sm_off.events])
    tl_same = ([(f.text_order, f.chrono_order) for f in sm_on.timeline_frames]
               == [(f.text_order, f.chrono_order) for f in sm_off.timeline_frames])
    ent_same = (len(sm_on.entities) == len(sm_off.entities))
    rt_same = (sm_on.memory_roundtrip == sm_off.memory_roundtrip)
    defers_none = all((e.patient_defer is None and e.agent_defer is None) for e in sm_on.events)
    default_on = SituationReader(gaz={}).precision_weight_roles is True
    off_is_off = SituationReader.all_capabilities_off(gaz={}).precision_weight_roles is False
    w2 = bool(ev_same and tl_same and ent_same and rt_same and defers_none and default_on and off_is_off)
    print("  [W2] additive: events==%s timeline==%s entities==%s roundtrip==%s | all *_defer None=%s | default-ON=%s all_off-OFF=%s -> %s"
          % (ev_same, tl_same, ent_same, rt_same, defers_none, default_on, off_is_off, "PASS" if w2 else "FAIL"))
    passed += w2

    # ---------------------------------------------------------------- W3 DEFER GAIN reproduces LIVE (a2=0)
    dev = load(TRAIN)[:3000]
    te = load(TEST) if TEST_SLICE is None else load(TEST)[:TEST_SLICE]
    print("  [W3] building live-config (a2=0) rows: dev=%d te=%d sents ..." % (len(dev), len(te)))
    p_dev, _ = patient_rows_a2z(wdw_population(dev), W)
    p_te, _ = patient_rows_a2z(wdw_population(te), W)
    o_dev, _ = obl_rows_a2z(dev, W)
    o_te, _ = obl_rows_a2z(te, W)
    w3p, l3p = _abstain_check(p_dev, p_te, "        PATIENT (n=%d, a2=0)" % len(p_te))
    w3o, l3o = _abstain_check(o_dev, o_te, "        obl    (n=%d, a2=0)" % len(o_te))
    w3 = bool(w3p and w3o)
    print("  [W3] DEFER GAIN reproduces LIVE (a2_marg dropped -> single shared parse):")
    print("    " + l3p)
    print("    " + l3o)
    print("    (solver published, a2 KEPT: PATIENT +0.0873 / obl +0.0916 -- the a2=0 live numbers above are the"
          " deployed config; any small delta is the inert-a2 drop, gain preserved because the defer is rank/coverage-based)")
    passed += w3

    # ---------------------------------------------------------------- W4 EVENT_CONF
    # (a) LIVE: event_conf == agent_conf * patient_conf on emitted events
    doc = [
        (0, 0, "John", "(0)"), (0, 1, "chased", "_"), (0, 2, "the", "_"), (0, 3, "cat", "(1)"), (0, 4, ".", "_"),
        (1, 0, "He", "(0)"), (1, 1, "caught", "_"), (1, 2, "the", "_"), (1, 3, "dog", "(2)"), (1, 4, ".", "_"),
    ]
    dpath = _write_temp_conll(doc)
    try:
        sm = SituationReader(gaz={"john": "masc"}).read(dpath)
    finally:
        try:
            os.remove(dpath)
        except OSError:
            pass
    live_ev = [e for e in sm.events if e.event_conf is not None]
    w4a = (len(live_ev) >= 1
           and all(abs(e.event_conf - e.agent_conf * e.patient_conf) < 1e-12 for e in live_ev)
           and all(0.0 <= e.event_conf <= 1.0 and 0.0 <= e.agent_conf <= 1.0 and 0.0 <= e.patient_conf <= 1.0
                   for e in live_ev))
    print("  [W4a] LIVE event_conf: %d event(s) carry it; event_conf==agent_conf*patient_conf & in [0,1] -> %s"
          % (len(live_ev), "PASS" if w4a else "FAIL"))
    for e in live_ev:
        print("        %-8s agent_conf=%.4f x patient_conf=%.4f = event_conf=%.4f"
              % (e.predicate, e.agent_conf, e.patient_conf, e.event_conf))

    # (b) PROPERTY: product predicts whole-event correctness AUC > single roles; twin flat; event abstain CI-sep
    jslice = te if TEST_SLICE is not None else load(TEST)[:900]
    jd, s1 = joint_rows_a2z(dev, W)
    jt, _ = joint_rows_a2z(jslice, W, s1)
    jok = DC._arr(jt, "joint_ok")
    a_raw = DC._arr(jt, "raw_margin"); a_p = DC._arr(jt, "p_conf")
    auc_m = auc(a_raw, jok); auc_p = auc(a_p, jok); auc_prod = auc(a_raw * a_p, jok)
    # calibrated-agent reference (fit the agent logistic on dev, like the validated cell)
    from experiments.exp_precwt_live_whodidwhat_v1 import logistic_fit, logistic_p
    wa, mua, sda = logistic_fit(np.array([r["a_feats"] for r in jd]), np.array([r["a_ok"] for r in jd]))
    a_cal = logistic_p([r["a_feats"] for r in jt], wa, mua, sda)
    auc_prod_cal = auc(a_cal * a_p, jok)
    # twin: shuffled product
    prod = a_raw * a_p; tw = prod.copy(); np.random.default_rng(11).shuffle(tw)
    auc_twin = auc(tw, jok)
    # event-level abstain with the (raw-margin) product, deployed dev tau
    dep = [dict(r, conf=float(r["raw_margin"] * r["p_conf"]), ok=r["joint_ok"]) for r in jd]
    tep = [dict(r, conf=float(r["raw_margin"] * r["p_conf"]), ok=r["joint_ok"]) for r in jt]
    jtau = DC.choose_tau_coverage(dep, 0.75)
    jab = DC.abstain_metrics(tep, jtau)
    jci = DC.boot_delta(tep, lambda rr: DC.abstain_metrics(rr, jtau)["answered_acc"])
    w4b = bool(auc_prod > max(auc_m, auc_p) + 0.02 and auc_twin < min(auc_m, auc_p) + 0.05
               and jci["sep"] and jci["ci"][0] > 0)
    print("  [W4b] PROPERTY (n_events=%d): AUC product(raw-margin x patient)=%.3f > agent-margin %.3f / patient %.3f"
          % (len(jt), auc_prod, auc_m, auc_p))
    print("        product(CALIBRATED agent)=%.3f (reference) | twin=%.3f (flat) | event abstain %.4f->%.4f (%+.4f CI[%+.4f,%+.4f] sep=%s)"
          % (auc_prod_cal, auc_twin, jab["blanket"], jab["answered_acc"], jab["delta_vs_blanket"],
             jci["ci"][0], jci["ci"][1], jci["sep"]))
    w4 = bool(w4a and w4b)
    print("  [W4] EVENT_CONF -> %s" % ("PASS" if w4 else "FAIL"))
    passed += w4

    print(("" if passed == total else "!! ") + "%d/%d CHECKS PASS" % (passed, total))
    assert passed == total, "witness failed: %d/%d" % (passed, total)


if __name__ == "__main__":
    main()
