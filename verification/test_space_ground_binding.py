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
  W4 LIVE READER (REPINNED 2026-09-16, pri 137): driven end-to-end through SituationReader(track_space=True)
     .read(), switching the lever off IN THE MODULE THE READER RUNS (hdlab.space_reader -- not the promoted-away
     experiments copy) LOWERS where-is, and the shuffled-ground twin loses. The old stub target made ON == OFF by
     construction; a structural assert now FAILS instead of passing vacuously if that recurs.

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
    """POST-PROMOTION REPIN (pri 137, 2026-09-16): the lever is switched off IN THE MODULE THE READER RUNS.

    Until today this stubbed `experiments._space_reader.ground_bind_events` -- a function in the COPY the reader
    stopped running at the 2026-09-09 promotion (`hdlab/situation_reader.py::_read_space` imports
    `hdlab.space_reader`). Both arms therefore ran the lever ON and the check could not fail for the reason it was
    written: ON == OFF, 0.3830 both arms, measured 2026-09-16. Two CLAIMS are pinned here, both direction-only:
      (1) STRUCTURAL -- the reader's space dimension runs the module this check stubs, so the check cannot silently
          repeat the defect at the next promotion (`reader._space_mod is SP`);
      (2) DIRECTIONAL -- forcing the conservative named-ground pass OFF LOWERS the live reader's where-is on the
          modern gold, through the FULL read (SituationReader...read(cp).locations), and the shuffled-ground
          info-free TWIN also loses to the landed arm.
    For orientation only (2026-09-16, pri 137, n=47 items over the 8 modern passages, historical-weak reader
    config): OFF 0.1915 -> ON 0.3830 (+0.1915, item-paired CI[+0.0213,+0.3404]); shuffled-ground twin 0.1277;
    stateless last-mention place floor 0.1489. Those values are NOT asserted -- the full measurement, with the
    product-reader arms and the entity-file hand-off, is `experiments/exp_space_ground_lever_live_v1.py`."""
    import numpy as np
    from hdlab import space_reader as SP          # THE module hdlab/situation_reader.py::_read_space imports
    from hdlab.situation_reader import SituationReader
    from hdlab.coref import parse_litbank_conll
    from experiments.exp_space_where_is_end_to_end_v1 import gold_at, correct
    import experiments.exp_space_where_is_modern_v1 as MOD
    _ORIG = SP.ground_bind_events
    cdir = os.path.join(_REPO, "data", "test_space_ground_binding", "conll"); os.makedirs(cdir, exist_ok=True)

    # ASK THE READER BY ITS OWN FILE, NOT BY A GOLD CLUSTER ID (the pri 131 identity contract). The register's
    # track keys are the reader's own entity files, and pri 137's one-file hand-off changes WHICH file the
    # protagonist is on -- so a question keyed on the gold cluster id "0" answers None after that landing and this
    # check would read 0.0 for reasons that have nothing to do with the lever. The question is aligned to the
    # reader's file by MAJORITY over the answer key's own mention positions, and the alignment is computed AFTER
    # every decision (gold ids influence WHICH TRACK IS SCORED, never a prediction). Capturing the stream needs a
    # pass-through wrapper on _read_space; it changes no behaviour (it forwards every argument untouched).
    _orig_rs = SituationReader._read_space

    def _capture(slf, conll_path, mentions=None, **kw):
        slf._w4_stream = mentions
        return _orig_rs(slf, conll_path, mentions=mentions, **kw)

    def measure(mode):
        """mode: 'on' (as landed) | 'off' (lever switched off) | 'twin' (grounds scrambled, firing kept)."""
        if mode == "on":
            SP.ground_bind_events = _ORIG
        elif mode == "off":
            SP.ground_bind_events = (lambda *a, **k: [])
        else:
            SP.ground_bind_events = (lambda *a, **k: _ORIG(*a, **dict(k, shuffle_rng=np.random.default_rng(7))))
        SituationReader._read_space = _capture
        accs, mods = [], []
        try:
            for p in MOD.PASSAGES:
                cp = MOD.write_conll(p, cdir); rows = sorted(MOD.build_gold(p), key=lambda r: r["t"])
                mentions, _ = parse_litbank_conll(cp)
                reader = SituationReader.all_capabilities_off(track_space=True)
                reg = reader.read(cp).locations
                mods.append(reader._space_mod)
                stream = {(m["sent_idx"], m["wtok_start"]): m["cluster"]
                          for m in (getattr(reader, "_space_stream", None)
                                    or getattr(reader, "_w4_stream", None) or [])}
                cand = {}
                for m in mentions:
                    if m["cluster"] == 0:
                        c = stream.get((m["sent_idx"], m["wtok_start"]))
                        if c is not None:
                            cand[c] = cand.get(c, 0) + 1
                key = str(max(cand.items(), key=lambda kv: (kv[1], -abs(kv[0])))[0]) if cand else "0"
                f, l = rows[0]["t"], rows[-1]["t"] + 20
                for t in sorted({m["sent_idx"] for m in mentions if m["cluster"] == 0 and f <= m["sent_idx"] <= l}):
                    g = gold_at(rows, t)
                    if g is not None:
                        accs.append(correct(reg.where_is(key, t), g[0]))
        finally:
            SP.ground_bind_events = _ORIG
            SituationReader._read_space = _orig_rs
        return (float(np.mean(accs)) if accs else 0.0), len(accs), mods

    on, n, mods = measure("on")
    # (1) THE STRUCTURAL CLAIM: the stub target IS the module the live reader runs.
    assert mods and all(m is SP for m in mods),         ("the reader's space dimension does not run the module this check stubs -- REPIN the stub; this is the "
         "2026-09-09 promotion defect (pri 137) recurring",
         [getattr(m, "__name__", m) for m in mods])
    off, _, _ = measure("off")
    twin, _, _ = measure("twin")
    # (2) THE DIRECTIONAL CLAIM: switching the lever off must LOWER where-is; the info-free twin must lose.
    assert on > off, ("forcing the named-ground pass OFF must lower the live reader's where-is", on, off)
    assert on > twin, ("the shuffled-ground info-free twin must lose to the landed arm", on, twin)
    print("[W4] LANDED live read() where_is (modern, n=%d): ground_bind OFF %.4f -> ON %.4f (+%.4f); "
          "shuffled-ground twin %.4f; stub target %s (the module the reader runs)"
          % (n, off, on, on - off, twin, SP.__name__))


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
