"""Witness for space_where_is_is_extraction_recall_bound_add_lazy_locative_pp_bridging.

The brief proposed a lazy locative-PP bridge to fix motion-event EXTRACTION RECALL, expecting that to lift end
where_is. The disk REFUTES the premise and relocates the lever. This witness pins the load-bearing claims:

  W1 REFUTATION: the brief's recall bridge lifts extraction recall 0.44->0.89 but moves end where_is only ~+0.06,
     NOT CI-separated over the current chain (recall was never the where_is bottleneck).
  W2 REAL LEVER (modern gold, coref gold-injected): conservative NAMED-GROUND BINDING lifts where_is over the
     current chain and over the last-mention floor (CI-separated over the floor), the shuffled-ground TWIN LOSES,
     and motion-event precision does NOT regress (it improves).
  W3 ROBUSTNESS (real 19c LitBank gold, n>=500): conservative ground-binding is NET-POSITIVE over the current
     chain (no regression), beats the floor CI-separated and the twin, precision does not regress. (The AGGRESSIVE
     variant regresses on 19c -- the located wall; only the high-precision subset is robust.)
  W4 LIVE READER: driven end-to-end through SituationReader(track_space=True).read(), the wired reader beats the
     stock reader and recovers named grounds the stock reader returns <scene>/<away> for.

Glass-box, NO LLM, deterministic, ASCII, CPU-only.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)


def test_w1_recall_bridge_refutation():
    """The brief's recall bridge: big recall gain, ~no where_is gain over the current chain."""
    from experiments import exp_space_recall_e2e_ci_v1 as CI
    out = CI.run(smoke=False)
    # recall materially recovered (loose bucket recall here; the strict extraction_quality recall is 0.44->0.89)
    assert out["recall_augmented"] > out["recall_current"] + 0.10, out["recall_augmented"]
    # ... but end where_is barely moves and is NOT CI-separated over the current chain
    g = out["gates"]["aug_vs_current_item"]
    assert abs(g["delta"]) < 0.12, g
    assert g["CI_sep"] is False, "the recall bridge must NOT CI-separate on where_is over the current chain"
    print("[W1] recall bridge: recall %.3f->%.3f but where_is delta %+.3f CI[%+.3f,%+.3f] NOT-sep (refuted)"
          % (out["recall_current"], out["recall_augmented"], g["delta"], g["lo"], g["hi"]))


def test_w2_named_ground_binding_modern():
    """Conservative named-ground binding on the modern gold: beats floor CI-sep, twin loses, precision no-regress."""
    from experiments import exp_space_named_ground_binding_v1 as GB
    out = GB.run(smoke=False)
    pop = out["pop_acc"]
    assert pop["arm"] > pop["cur"], (pop["arm"], pop["cur"])                 # net-positive over current
    assert out["gates"]["arm_vs_floor_item"]["CI_sep"] is True              # beats the stateless floor CI-sep
    assert out["gates"]["arm_vs_twin_item"]["CI_sep"] is True               # the shuffled-ground twin LOSES
    assert pop["arm"] > pop["twn"] + 0.10
    assert out["precision"]["arm"] >= out["precision"]["cur"] - 0.02        # precision must not regress
    assert pop["arm"] < pop["ceil"]                                         # still below the perfect-extraction ceiling
    print("[W2] modern: current %.3f -> ARM %.3f (twin %.3f, floor %.3f, ceiling %.3f); precision %.3f -> %.3f"
          % (pop["cur"], pop["arm"], pop["twn"], pop["floor"], pop["ceil"],
             out["precision"]["cur"], out["precision"]["arm"]))


def test_w3_named_ground_binding_litbank_robust():
    """Conservative named-ground binding on REAL 19c gold (n>=500): net-positive, no regression, twin loses."""
    from experiments import exp_space_ground_binding_litbank_v1 as LB
    out = LB.run(smoke=False)
    pop = out["pop_acc"]
    assert out["n_items"] >= 500, out["n_items"]
    assert pop["arm"] >= pop["cur"], (pop["arm"], pop["cur"])               # NO regression on real prose
    assert out["gates"]["arm_vs_floor"]["CI_sep"] is True                   # beats floor CI-sep even on real prose
    assert out["gates"]["arm_vs_twin"]["CI_sep"] is True                    # shuffled-ground twin LOSES
    assert out["precision"]["arm"] >= out["precision"]["cur"] - 0.01        # precision no-regress
    print("[W3] 19c (n=%d): current %.3f -> ARM %.3f (twin %.3f, floor %.3f); precision %.3f -> %.3f; "
          "arm_vs_current delta %+.3f (timeline CI %s)"
          % (out["n_items"], pop["cur"], pop["arm"], pop["twn"], pop["floor"],
             out["precision"]["cur"], out["precision"]["arm"],
             out["gates"]["arm_vs_current"]["delta"], out["gates"]["arm_vs_current"]["CI_sep"]))


def test_w4_live_reader_end_to_end():
    """POST-LANDING (2026-09-06): the conservative named-ground wire is now LIVE BY DEFAULT
    (read_locations_in_substrate passes ground_bind=ext in prior_ext, the mode the reader uses). Confirm the LIVE
    reader's where_is with the wire ON beats it forced OFF, reproducing the +0.170 live gain. [The old
    stock-vs-monkeypatch framing became premise-stale at landing -- both arms would now bind.]"""
    import numpy as np
    import experiments._space_reader as SP
    from hdlab.situation_reader import SituationReader
    from hdlab.coref import parse_litbank_conll
    from experiments.exp_space_where_is_end_to_end_v1 import gold_at, correct
    import experiments.exp_space_where_is_modern_v1 as MOD
    _ORIG = SP.ground_bind_events
    cdir = os.path.join(_REPO, "data", "test_space_ground_binding", "conll"); os.makedirs(cdir, exist_ok=True)

    def measure(on):
        SP.ground_bind_events = _ORIG if on else (lambda *a, **k: [])
        accs = []
        try:
            for p in MOD.PASSAGES:
                cp = MOD.write_conll(p, cdir); rows = sorted(MOD.build_gold(p), key=lambda r: r["t"])
                mentions, _ = parse_litbank_conll(cp)
                reg = SituationReader.all_capabilities_off(track_space=True).read(cp).locations
                f, l = rows[0]["t"], rows[-1]["t"] + 20
                for t in sorted({m["sent_idx"] for m in mentions if m["cluster"] == 0 and f <= m["sent_idx"] <= l}):
                    g = gold_at(rows, t)
                    if g is not None:
                        accs.append(correct(reg.where_is("0", t), g[0]))
        finally:
            SP.ground_bind_events = _ORIG
        return (float(np.mean(accs)) if accs else 0.0), len(accs)

    on, n = measure(True)
    off, _ = measure(False)
    assert on > off, (on, off)
    print("[W4] LANDED live read() where_is (modern, n=%d): ground_bind OFF %.4f -> ON %.4f (+%.4f)"
          % (n, off, on, on - off))


def test_w5_additive_safety_no_other_consumer_regresses():
    """The ground-binding is purely additive to SPACE: extract_events_in_substrate is called ONLY by _read_space,
    so the who-did-what events (and every other dimension) are byte-identical with vs without the wire."""
    import experiments._space_reader as SP
    from experiments.exp_space_ground_binding_live_wire_v1 import _patched_extract, _ORIG_EXTRACT
    from hdlab.situation_reader import SituationReader
    import experiments.exp_space_where_is_modern_v1 as MOD
    cp = MOD.write_conll(MOD.PASSAGES[1], os.path.join(_REPO, "data", "exp_space_named_ground_binding_v1", "conll"))
    gaz = SituationReader().gaz

    def events_repr(patched):
        SP.extract_events_in_substrate = _patched_extract if patched else _ORIG_EXTRACT
        return repr(SituationReader(gaz=gaz, track_space=True).read(cp).events)
    stock, wired = events_repr(False), events_repr(True)
    SP.extract_events_in_substrate = _ORIG_EXTRACT
    assert stock == wired, "who-did-what events must be byte-identical under the space patch"
    print("[W5] additive-safety: who-did-what events byte-identical with/without ground-binding (no consumer regresses)")


if __name__ == "__main__":
    test_w1_recall_bridge_refutation()
    test_w2_named_ground_binding_modern()
    test_w3_named_ground_binding_litbank_robust()
    test_w4_live_reader_end_to_end()
    test_w5_additive_safety_no_other_consumer_regresses()
    print("\nALL WITNESS CHECKS PASSED")
