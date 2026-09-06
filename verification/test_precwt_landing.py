"""Witness for the LANDED precision-weighting wire (owner-DONE
precision_weight_the_head_driven_readers_on_calibrated_parse_confidence, Q111 strategy landing).

Unlike verification/test_precwt_live_readers_organ.py (which RE-FITS the calibrator each run to re-derive the
prototype), THIS witness drives the LANDED artifacts:
  * hdlab.parse_confidence -- the FROZEN offline calibrators (patient full / parse-only / obl), baked as literals.
  * hdlab.situation_reader precision_weight_roles -- the live reader exposing EventRecord.patient_conf / .defer.

W1 (LIVE reader exposes the precision-weighted/defer readout + risk-coverage): a SituationReader built with
    precision_weight_roles=True attaches a calibrated patient reliability in [0,1] to its wired events and a
    defer flag at tau; the default reader (flag OFF) attaches None. On modern gold the confidence RANKS the live
    patient reader right-from-wrong (selective accuracy rises monotonically on the confident subset).
W2 (the headline numbers reproduced THROUGH THE FROZEN calibrator, random twin flat): scoring the validated
    who-did-what / obl rows with the LANDED frozen weights reproduces UD-EWT patient sel@50 0.8789->0.9745
    (+0.0956) / QA-SRL 0.2982->0.3414 (+0.0432) / obl 0.7581->0.8919 (+0.1338), each CI-separated with the
    random-confidence twin FLAT (its sel@50 CI upper bound = the null-p95, cleared 5-9x).
W3 (ADDITIVE-SAFETY): reading a real doc with the flag ON vs OFF leaves the parse heads AND every SituationModel
    dim byte-identical -- only the new patient_conf / patient_defer metadata is added (no scored dim regresses).

Glass-box, deterministic, NO LLM, ASCII. Fast: the frozen calibrator needs NO train build / no re-fit.
Run: .venv/Scripts/python.exe verification/test_precwt_landing.py
"""
from __future__ import annotations
import os, sys, glob, json

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import numpy as np

import hdlab.arceager_parser as AE
from hdlab.arc_parser import ArcParser
from hdlab import parse_confidence as PC
from hdlab.situation_reader import SituationReader
import experiments.exp_precwt_live_whodidwhat_v1 as WDW
import experiments.exp_precwt_live_obl_space_v1 as OBL
from experiments.exp_typed_selpref_ppattach_v1 import load, TEST

ARC2 = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
QASRL = os.path.join(_REPO, "data/exp_noncanonical_role_diagnostic_v1/aligned_gold.jsonl")


def _pick_doc():
    for cand in ("158_emma_brat.conll", "105_persuasion_brat.conll"):
        p = os.path.join(_REPO, "data/litbank/coref/conll", cand)
        if os.path.exists(p):
            return p
    hits = sorted(glob.glob(os.path.join(_REPO, "data/litbank/coref/conll", "*.conll")))
    return hits[0] if hits else None


def risk_coverage(ok, conf):
    order = np.argsort(-np.asarray(conf, float)); n = len(ok); out = []
    for cov in (0.1, 0.25, 0.5, 0.75, 1.0):
        k = max(1, int(cov * n)); out.append(round(float(np.asarray(ok)[order[:k]].mean()), 4))
    return out


def main():
    print("witness: LANDED precision-weighting wire (frozen calibrator + live reader exposure + additive safety)")
    W = AE.load_model(AE.MODEL_PATH); ap = ArcParser.load(ARC2)

    # ============================ W1: the LIVE reader exposes the readout ============================
    doc = _pick_doc()
    assert doc is not None, "W1 FAIL: no litbank conll doc found"
    off = SituationReader(gaz={}).read(doc)                                   # default -> flag OFF
    on = SituationReader(gaz={}, precision_weight_roles=True, precision_weight_tau=0.5).read(doc)
    assert len(off.events) == len(on.events), "W1 FAIL: event count changed"
    assert all(e.patient_conf is None and e.patient_defer is None for e in off.events), \
        "W1 FAIL: default reader must not populate patient_conf/defer"
    pop = [e for e in on.events if e.patient_conf is not None]
    assert pop, "W1 FAIL: precision_weight_roles=True populated no patient_conf"
    assert all(0.0 <= e.patient_conf <= 1.0 for e in pop), "W1 FAIL: patient_conf out of [0,1]"
    assert any(e.patient_defer for e in pop) and any(not e.patient_defer for e in pop), \
        "W1 FAIL: defer flag not exercised on both sides of tau"
    print("  W1a PASS: live reader exposes patient_conf in [0,1] on %d/%d events (defer flag live); OFF reader all-None"
          % (len(pop), len(on.events)))

    # risk-coverage of the LIVE patient reader on modern gold, ranked by the LANDED frozen confidence
    te = load(TEST)
    rows = WDW.build_rows(te, W, ap, is_qa=False)
    ok = np.array([r["ok"] for r in rows])
    conf = np.array([PC.patient_confidence(r) for r in rows])
    rc = risk_coverage(ok, conf)
    print("  W1b risk-coverage (selective patient acc @ cov 10/25/50/75/100%%): %s" % rc)
    assert rc[0] >= rc[2] >= rc[4] and rc[2] > rc[4], "W1 FAIL: selective accuracy not monotone in confidence"
    print("  W1b PASS: selective accuracy rises on the confident subset (%.4f @10%% vs %.4f blanket)" % (rc[0], rc[4]))

    # ============================ W2: headline reproduced through the FROZEN calibrator ============================
    def sel(rows, conf):
        ok = np.array([r["ok"] for r in rows]); s = WDW.sel_at(ok, conf)
        rng = np.random.default_rng(11); tw = conf.copy(); rng.shuffle(tw); tws = WDW.sel_at(ok, tw)
        return float(ok.mean()), s, tws

    # UD-EWT patient (frozen full calibrator)
    b, s, tws = sel(rows, conf)
    auc_raw = WDW.auc(np.array([r["ae_conf"] for r in rows]), ok); auc_cal = WDW.auc(conf, ok)
    print("  [UD-EWT patient] n=%d blanket=%.4f AUC raw=%.3f cal=%.3f | sel@50=%.4f(%+.4f CI%s) twin=%.4f(%+.4f) null-p95=%+.4f"
          % (len(rows), b, auc_raw, auc_cal, s[0], s[1], s[2], tws[0], tws[1], tws[2][1]))
    assert len(rows) == 1255 and abs(b - 0.8789) < 5e-4, "W2 FAIL: UD-EWT population drift (n=%d b=%.4f)" % (len(rows), b)
    assert abs(s[0] - 0.9745) < 2e-3 and abs(s[1] - 0.0956) < 2e-3, "W2 FAIL: UD-EWT sel@50 not reproduced (%s)" % (s,)
    assert s[2][0] > tws[2][1] and abs(tws[1]) <= tws[2][1] + 1e-9, "W2 FAIL: UD-EWT twin not flat below the effect"

    # QA-SRL patient (frozen full calibrator)
    qa = [json.loads(l) for l in open(QASRL, encoding="utf-8")]
    qrows = WDW.build_rows(qa, W, ap, is_qa=True)
    qconf = np.array([PC.patient_confidence(r) for r in qrows]); qok = np.array([r["ok"] for r in qrows])
    qb, qs, qtws = sel(qrows, qconf)
    print("  [QA-SRL patient] n=%d blanket=%.4f AUC cal=%.3f | sel@50=%.4f(%+.4f CI%s) twin=%.4f(%+.4f)"
          % (len(qrows), qb, WDW.auc(qconf, qok), qs[0], qs[1], qs[2], qtws[0], qtws[1]))
    assert len(qrows) == 8225 and abs(qb - 0.2982) < 5e-4, "W2 FAIL: QA-SRL population drift"
    assert abs(qs[0] - 0.3414) < 2e-3 and abs(qs[1] - 0.0432) < 2e-3, "W2 FAIL: QA-SRL sel@50 not reproduced (%s)" % (qs,)
    assert qs[2][0] > qtws[2][1], "W2 FAIL: QA-SRL twin not below the effect"
    print("  W2a PASS: who-did-what patient headline reproduced through the FROZEN calibrator (UD + QA-SRL), twin flat")

    # obl/spatial attachment (frozen obl calibrator)
    orows = OBL.obl_rows(te, W, ap)
    oconf = np.array([PC.obl_confidence(r) for r in orows]); ook = np.array([r["ok"] for r in orows])
    ob, os_, otws = sel(orows, oconf)
    print("  [UD-EWT obl] n=%d blanket=%.4f AUC cal=%.3f | sel@50=%.4f(%+.4f CI%s) twin=%.4f(%+.4f)"
          % (len(orows), ob, WDW.auc(oconf, ook), os_[0], os_[1], os_[2], otws[0], otws[1]))
    assert len(orows) == 2294 and abs(ob - 0.7581) < 5e-4, "W2 FAIL: obl population drift"
    assert abs(os_[0] - 0.8919) < 2e-3 and abs(os_[1] - 0.1338) < 2e-3, "W2 FAIL: obl sel@50 not reproduced (%s)" % (os_,)
    assert os_[2][0] > otws[2][1], "W2 FAIL: obl twin not below the effect"
    print("  W2b PASS: SECOND head-driven reader (obl/spatial) headline reproduced through the frozen calibrator, twin flat")

    # ============================ W3: additive-safety (byte-identical ON vs OFF) ============================
    def dims(sm):
        return {
            "events": [(e.agent, e.patient, e.predicate, e.tense, e.sent_idx, e.subj_role, e.obj_role, e.affect,
                        e.patient_is_bare_do) for e in sm.events],
            "coref": [(r.correct, getattr(r, "sent_dist", None)) for r in (sm.coref_resolutions or [])],
            "coref_acc": sm.coref_acc,
            "timeline": [(f.sent_idx, tuple(f.chrono_order)) for f in (sm.timeline_frames or [])],
            "timeline_order": sm.timeline_order,
            "causal": [(c.sent_idx, c.cause, c.outcome, c.method) for c in (sm.causal_links or [])],
            "memory": sm.memory_roundtrip,
            "suppressed": [(s.sent_idx, s.predicate) for s in (sm.suppressed_predicates or [])],
        }
    do, dn = dims(off), dims(on)
    for k in do:
        assert do[k] == dn[k], "W3 FAIL: dim '%s' changed ON vs OFF (additive-safety broken)" % k
    print("  W3a PASS: every SituationModel dim (events/coref/timeline/causal/memory/suppressed) byte-identical ON vs OFF")

    # parse heads unchanged (the additive claim): exposing conf/marg changes no head
    n_head_changed = 0; n_checked = 0
    for s in te[:300]:
        toks = [t[1] for t in s]; pos = [t[3] for t in s]
        h1 = AE.parse_with_conf(toks, pos, W)[0]
        h2, c2, m2 = AE.parse_with_conf(toks, pos, W)
        n_checked += 1
        if h1 != h2:
            n_head_changed += 1
    assert n_head_changed == 0, "W3 FAIL: parse heads not deterministic/additive (%d changed)" % n_head_changed
    print("  W3b PASS: parse_with_conf heads deterministic + read-only over %d sents -- confidence is ADDITIVE (no head change)"
          % n_checked)

    print("ALL CHECKS PASS (W1 W2 W3)")


if __name__ == "__main__":
    main()
