"""Scaffold-free witness: a DEFER-CONSUMER that ACTS on the landed calibrated parse confidence (abstain below a
DEV-chosen tau) lifts LIVE comprehension reliability on MODERN gold, twin-controlled, additively -- and the two
located negatives (fall-back; the upstream small-beam) are reproduced and well-attributed.

Re-derives the headline from the substrate's OWN parser + the DEPLOYED readers + the FROZEN hdlab.parse_confidence
calibrator on a UD-EWT slice (tau chosen on TRAIN, applied on full TEST). Fast. Asserts:

  W1 (PATIENT abstain): deploying tau (dev) so the reader ABSTAINS on the shaky arcs lifts accuracy-on-ANSWERED
      CI-separated above the blanket reader, and the random-confidence TWIN at matched coverage does NOT.
  W2 (OBL abstain): same, on obl/spatial attachment.
  W3 (FALL-BACK located negative, well-attributed): fall-back to a head-independent prior does NOT beat blanket
      (patient: position is a worse reader; obl: the parser beats locality even on its shakiest quartile).
  W4 (UPSTREAM small-beam located negative): a faithful k-beam decode's reliability readouts are <= the greedy
      raw arc conf, and gold is in the beam on < 60% of the parser's WRONG arcs (half the errors are search
      failures) -- so no beam width yields a better posterior (label bias; the north-star is global normalization).
  W5 (read-cost / flip-on): the calibrated confidence comes from ONE parse (parse_with_conf returns heads+conf+
      marg together), and the global arc_parser a2_marg cue is droppable for obl (AUC cost < 0.01) -> the defer
      path needs no extra parse.
  W6 (ADDITIVE / no-regress): tau=None (blanket) is byte-identical to the current reader (defer never fires).

Run: .venv/Scripts/python.exe verification/test_defer_consumer_organ.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import numpy as np

import hdlab.arceager_parser as AE
from hdlab.arc_parser import ArcParser
from hdlab import parse_confidence as PC
from experiments.exp_typed_selpref_ppattach_v1 import load, TRAIN, TEST
from experiments.exp_precision_weighted_whodidwhat_v1 import wdw_population
import experiments.exp_defer_consumer_v1 as DC
import experiments.exp_defer_upstream_smallbeam_v1 as BEAM
import experiments.exp_defer_density_sweep_v1 as DEN
import experiments.exp_defer_agent_v1 as AG
import experiments.exp_defer_joint_event_v1 as JE
from experiments.exp_precwt_live_whodidwhat_v1 import logistic_fit as _lfit, logistic_p as _lp
from experiments.exp_precwt_live_agent_v1 import _feats as _agfeats


def main():
    print("witness: DEFER-CONSUMER acting on the landed calibrated parse confidence (modern gold)")
    W = AE.load_model(AE.MODEL_PATH)
    ARC2 = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
    ap = ArcParser.load(ARC2)
    dev = load(TRAIN)[:3000]; te = load(TEST)
    passed = 0; total = 9

    # ---- build LIVE rows (patient + obl) ----
    p_dev, _ = DC.patient_rows(wdw_population(dev), W, ap, False)
    p_te, _ = DC.patient_rows(wdw_population(te), W, ap, False)
    o_dev, _ = DC.obl_rows(dev, W, ap)
    o_te, _ = DC.obl_rows(te, W, ap)

    # ---- W1 PATIENT abstain ----
    tau = DC.choose_tau_coverage(p_dev, 0.75)
    ab = DC.abstain_metrics(p_te, tau); ci = DC.boot_delta(p_te, lambda rr: DC.abstain_metrics(rr, tau)["answered_acc"])
    tw = DC._twin_conf(p_te); tau_tw = float(np.quantile(DC._arr(DC._twin_conf(p_dev), "conf_twin"), 0.25))
    tw_ab = DC.abstain_metrics([dict(r, conf=r["conf_twin"]) for r in tw], tau_tw)
    w1 = (ci["sep"] and ci["ci"][0] > 0 and ci["ci"][0] > tw_ab["delta_vs_blanket"])
    print("  [W1] PATIENT abstain (tau=%.3f cov=%.3f): answered=%.4f (%+.4f CI[%+.4f,%+.4f]) vs blanket %.4f | twin %+.4f -> %s"
          % (tau, ab["coverage"], ab["answered_acc"], ab["delta_vs_blanket"], ci["ci"][0], ci["ci"][1],
             ab["blanket"], tw_ab["delta_vs_blanket"], "PASS" if w1 else "FAIL"))
    passed += w1

    # ---- W2 OBL abstain ----
    otau = DC.choose_tau_coverage(o_dev, 0.75)
    oab = DC.abstain_metrics(o_te, otau); oci = DC.boot_delta(o_te, lambda rr: DC.abstain_metrics(rr, otau)["answered_acc"])
    otw = DC._twin_conf(o_te); otau_tw = float(np.quantile(DC._arr(DC._twin_conf(o_dev), "conf_twin"), 0.25))
    otw_ab = DC.abstain_metrics([dict(r, conf=r["conf_twin"]) for r in otw], otau_tw)
    w2 = (oci["sep"] and oci["ci"][0] > 0 and oci["ci"][0] > otw_ab["delta_vs_blanket"])
    print("  [W2] OBL abstain (tau=%.3f cov=%.3f): answered=%.4f (%+.4f CI[%+.4f,%+.4f]) vs blanket %.4f | twin %+.4f -> %s"
          % (otau, oab["coverage"], oab["answered_acc"], oab["delta_vs_blanket"], oci["ci"][0], oci["ci"][1],
             oab["blanket"], otw_ab["delta_vs_blanket"], "PASS" if w2 else "FAIL"))
    passed += w2

    # ---- W3 FALL-BACK located negative ----
    ptf, _ = DC.choose_tau_fallback(p_dev); p_fb = DC.fallback_acc(p_te, ptf); p_bl = float(DC._arr(p_te, "ok").mean())
    otf, _ = DC.choose_tau_fallback(o_dev)
    o_conf = DC._arr(o_te, "conf"); shaky = o_conf <= float(np.quantile(o_conf, 0.25))
    parse_shaky = float(DC._arr(o_te, "ok")[shaky].mean()); loc_shaky = float(DC._arr(o_te, "prior_ok")[shaky].mean())
    w3 = (p_fb <= p_bl + 0.002) and (parse_shaky > loc_shaky)
    print("  [W3] FALL-BACK negative: patient pos fall-back=%.4f<=blanket=%.4f | obl shaky-quartile parse=%.4f > locality=%.4f -> %s"
          % (p_fb, p_bl, parse_shaky, loc_shaky, "PASS" if w3 else "FAIL"))
    passed += w3

    # ---- W4 UPSTREAM small-beam located negative ----
    sl = te[:400]
    pb = BEAM.patient_beam_rows(wdw_population(sl), W, ap, False, k=8)
    ob = BEAM.obl_beam_rows(sl, W, ap, k=8)
    pk_ok = np.array([r["ok"] for r in pb]); ob_ok = np.array([r["ok"] for r in ob])
    auc_raw = BEAM.auc(np.array([r["raw_conf"] for r in pb]), pk_ok)
    auc_beam = BEAM.auc(np.array([r["beam_rel"] for r in pb]), pk_ok)
    wrong = [r for r in ob if r["ok"] == 0]
    gib_wrong = float(np.mean([r["gold_in_beam"] for r in wrong])) if wrong else 1.0
    w4 = (auc_beam <= auc_raw + 0.01) and (gib_wrong < 0.60)
    print("  [W4] UPSTREAM beam negative: patient beam AUC=%.3f <= raw greedy conf=%.3f | gold-in-beam-when-wrong=%.3f (<0.60 => search failure) -> %s"
          % (auc_beam, auc_raw, gib_wrong, "PASS" if w4 else "FAIL"))
    passed += w4

    # ---- W5 read-cost: one parse gives heads+conf+marg; a2_marg droppable for obl ----
    toks = [t[1] for t in te[0]]; pos = [t[3] for t in te[0]]
    heads, conf, marg = AE.parse_with_conf(toks, pos, W)
    one_parse_ok = (len(conf) > 0 and len(marg) > 0 and len(heads) > 0)
    # a2 drop cost on an obl slice: refit obl calibrator with vs without a2_marg
    from experiments.exp_precwt_live_whodidwhat_v1 import logistic_fit, logistic_p
    def obl_feats_rows(sents):
        Xf, Xn, y = [], [], []
        for s in sents:
            tk = [t[1] for t in s]; ps = [t[3] for t in s]; n = len(tk)
            gh = {t[0]: t[4] for t in s}; gr = {t[0]: t[5].split(":")[0] for t in s}
            hh, cf, mg = AE.parse_with_conf(tk, ps, W); pr = ap.parse(tk, ps)
            for t in s:
                c = t[0]
                if gr.get(c) not in ("obl", "nmod") or t[3] not in ("NOUN", "PROPN", "PRON"):
                    continue
                ph = hh.get(c, 0); nc = sum(1 for u in range(1, n + 1) if ps[u - 1] == "VERB") + 1
                a2 = float(pr.margins[c]) if 0 <= c < len(pr.margins) else 0.0
                f = [float(cf.get(c, 0.0)), np.tanh(float(mg.get(c, 0.0)) / 20.0), np.tanh(a2 / 5.0),
                     1.0 / (1.0 + abs(ph - c)), min(nc, 6) / 6.0]
                Xf.append(f); Xn.append(f[:2] + f[3:]); y.append(int(ph == gh.get(c)))
        return np.array(Xf), np.array(Xn), np.array(y)
    Xf, Xn, y = obl_feats_rows(dev[:2500]); Xft, Xnt, yt = obl_feats_rows(te)
    wf, mf, sf = logistic_fit(Xf, y); wn, mn, sn = logistic_fit(Xn, y)
    a_with = BEAM.auc(logistic_p(Xft, wf, mf, sf), yt); a_wo = BEAM.auc(logistic_p(Xnt, wn, mn, sn), yt)
    w5 = one_parse_ok and (abs(a_with - a_wo) < 0.01)
    print("  [W5] read-cost: one parse yields heads+conf+marg=%s | obl a2_marg drop AUC %.4f->%.4f (|d|=%.4f<0.01) -> %s"
          % (one_parse_ok, a_with, a_wo, abs(a_with - a_wo), "PASS" if w5 else "FAIL"))
    passed += w5

    # ---- W6 additive / no-regress: tau=None never defers -> blanket byte-identical ----
    never = all(PC.defer(r["conf"], None) is False for r in p_te[:200])
    ab_none = DC.abstain_metrics(p_te, -1e9)   # tau below all -> keep everything == blanket
    w6 = never and abs(ab_none["answered_acc"] - ab_none["blanket"]) < 1e-9
    print("  [W6] additive: defer(conf,None)==False for all=%s | tau=-inf answered==blanket (%.4f==%.4f) -> %s"
          % (never, ab_none["answered_acc"], ab_none["blanket"], "PASS" if w6 else "FAIL"))
    passed += w6

    # ---- W7 DENSITY phase: the abstain gain is LARGER in dense competition than sparse, conf AUC stable ----
    A = DEN.part_a(dev, te, W, ap)
    by = {s["stratum"].split()[0]: s for s in A["strata"]}
    sp = by.get("sparse"); dn = by.get("dense")
    w7 = (sp is not None and dn is not None and dn["abstain_delta"] > sp["abstain_delta"]
          and min(s["conf_auc"] for s in A["strata"]) > 0.65)
    if sp and dn:
        print("  [W7] density: abstain gain sparse=%+.4f -> dense=%+.4f (dense>sparse) | conf AUC stable (min %.3f) -> %s"
              % (sp["abstain_delta"], dn["abstain_delta"], min(s["conf_auc"] for s in A["strata"]), "PASS" if w7 else "FAIL"))
    else:
        print("  [W7] density: insufficient strata -> FAIL")
    passed += w7

    # ---- W8 AGENT defer-consumer (completes the channel; EFFICIENT -- raw margin, no calibration) ----
    ad, _ = AG.agent_rows(dev, False); au, _ = AG.agent_rows(te, False)
    atau = DC.choose_tau_coverage(ad, 0.75)
    aab = DC.abstain_metrics(au, atau); aci = DC.boot_delta(au, lambda rr: DC.abstain_metrics(rr, atau)["answered_acc"])
    aconf = DC._arr(au, "conf").copy(); rng = np.random.default_rng(11); rng.shuffle(aconf)
    adc = DC._arr(ad, "conf").copy(); np.random.default_rng(11).shuffle(adc)
    atw = DC.abstain_metrics([dict(r, conf=float(aconf[i])) for i, r in enumerate(au)], float(np.quantile(adc, 0.25)))
    w8 = aci["sep"] and aci["ci"][0] > 0 and aci["ci"][0] > atw["delta_vs_blanket"]
    print("  [W8] AGENT abstain (RAW margin, no calibration; tau=%.3f): answered=%.4f (%+.4f CI[%+.4f,%+.4f]) vs blanket %.4f | twin %+.4f -> %s"
          % (atau, aab["answered_acc"], aab["delta_vs_blanket"], aci["ci"][0], aci["ci"][1], aab["blanket"], atw["delta_vs_blanket"], "PASS" if w8 else "FAIL"))
    passed += w8

    # ---- W9 JOINT-EVENT precision propagation (product beats single roles; event defer CI-sep, twin flat) ----
    jd, s1 = JE.joint_population(dev, W, ap); jt, _ = JE.joint_population(te[:1200], W, ap, s1)
    wa, mua, sda = _lfit(np.array([r["a_feats"] for r in jd]), np.array([r["a_ok"] for r in jd]))
    for rows in (jd, jt):
        for r, x in zip(rows, _lp([r["a_feats"] for r in rows], wa, mua, sda)):
            r["a_conf"] = float(x)
    jok = DC._arr(jt, "joint_ok")
    a_a = BEAM.auc(DC._arr(jt, "a_conf"), jok); a_p = BEAM.auc(DC._arr(jt, "p_conf"), jok)
    a_prod = BEAM.auc(DC._arr(jt, "a_conf") * DC._arr(jt, "p_conf"), jok)
    tep = [dict(r, conf=float(r["a_conf"] * r["p_conf"]), ok=r["joint_ok"]) for r in jt]
    dep = [dict(r, conf=float(r["a_conf"] * r["p_conf"]), ok=r["joint_ok"]) for r in jd]
    jtau = DC.choose_tau_coverage(dep, 0.75); jab = DC.abstain_metrics(tep, jtau)
    jci = DC.boot_delta(tep, lambda rr: DC.abstain_metrics(rr, jtau)["answered_acc"])
    jc = DC._arr(tep, "conf").copy(); np.random.default_rng(11).shuffle(jc)
    jtw = DC.abstain_metrics([dict(r, conf=float(jc[i])) for i, r in enumerate(tep)], float(np.quantile(jc, 0.25)))
    w9 = (a_prod > max(a_a, a_p) + 0.02) and jci["sep"] and jci["ci"][0] > jtw["delta_vs_blanket"]
    print("  [W9] JOINT-EVENT: product AUC=%.3f > agent %.3f / patient %.3f | event defer %+.4f CI[%+.4f,%+.4f] twin %+.4f -> %s"
          % (a_prod, a_a, a_p, jab["delta_vs_blanket"], jci["ci"][0], jci["ci"][1], jtw["delta_vs_blanket"], "PASS" if w9 else "FAIL"))
    passed += w9

    print("%s ALL CHECKS PASS (%d/%d)" % ("" if passed == total else "!! ", passed, total) if passed == total
          else "!! %d/%d CHECKS PASSED" % (passed, total))
    assert passed == total, "witness failed: %d/%d" % (passed, total)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
