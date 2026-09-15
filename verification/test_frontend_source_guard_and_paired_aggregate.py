"""Witness for two hygiene repairs from the 2026-09-15 substrate evaluation (E09, E10).

E10: the frontend switchboard must REFUSE an unknown tag/heads source name (a typo used to fall through to the
     supervised stand-in silently -- perceptron tags / arc-eager heads -- and invalidate any BF claim of the run).
E09: the board aggregate must keep a missing comparator MISSING (it used to drop the None from the numerator but
     keep the row's items in the denominator, i.e. count the floor as zero and overstate the model's advantage).

Runs under pytest (test_* functions) AND standalone (python verification/<this file>).
"""
import ast, os, sys
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)


def _agg_fn():
    src = open(os.path.join(_REPO, "experiments", "exp_situation_model_qa_modern_v1.py"), encoding="utf-8").read()
    node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "_agg")
    ns = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), "<board _agg>", "exec"), ns)
    return ns["_agg"]


def test_unknown_tag_source_raises():
    from hdlab import frontend as F
    try:
        F.Tagger(source="evaluation_invalid_source")
    except ValueError as e:
        assert "unknown tag source" in str(e)
    else:
        raise AssertionError("Tagger accepted an unknown source name (would have selected the perceptron stand-in)")


def test_unknown_heads_source_raises():
    from hdlab import frontend as F
    try:
        F.Parser(source="evaluation_invalid_source")
    except ValueError as e:
        assert "unknown heads source" in str(e)
    else:
        raise AssertionError("Parser accepted an unknown source name (would have selected the arc-eager stand-in)")


def test_valid_sources_still_construct():
    from hdlab import frontend as F
    assert F.TAG_SOURCES == frozenset({"counts", "perceptron"})
    assert F.HEADS_SOURCES == frozenset({"attachment_arm", "arceager"})
    t = F.Tagger(source="counts"); assert t._lc is not None and t._pt is None
    p = F.Parser(source="attachment_arm"); assert p._AA is not None and p._ae is None


def test_unknown_temporal_tagger_raises():
    import os, subprocess
    env = dict(os.environ, HDLAB_TEMPORAL_TAGGER="evaluation_invalid_source", OMP_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-c", "import hdlab.temporal_model"], cwd=_REPO, env=env,
                       capture_output=True, text=True)
    assert r.returncode != 0 and "unknown HDLAB_TEMPORAL_TAGGER" in r.stderr, r.stderr[-400:]
    from hdlab import temporal_model as T
    assert T.TEMPORAL_TAGGER == "counts_penn" and T.TEMPORAL_TAGGERS == frozenset({"counts_penn", "perceptron"})


def test_aggregate_keeps_missing_comparator_missing():
    agg = _agg_fn()
    rows = {"A": {"n": 100, "model_acc": 0.6, "strongest_floor": 0.5, "twin_acc": 0.1},
            "B": {"n": 100, "model_acc": 0.6, "strongest_floor": None, "twin_acc": None}}
    out = agg(rows)
    assert out["model_acc"] == 0.6 and out["n"] == 200
    # the floor is averaged over the rows that HAVE one (row A only) -> 0.5, never 0.25
    assert out["strongest_floor"] == 0.5, out
    assert out["twin_acc"] == 0.1, out
    assert out["n_with_floor"] == 100 and out["n_with_twin"] == 100
    assert out["comparators_complete"] is False


def test_aggregate_unchanged_when_complete():
    agg = _agg_fn()
    rows = {"A": {"n": 100, "model_acc": 0.6, "strongest_floor": 0.5, "twin_acc": 0.1, "ci_sep_over_strongest": True},
            "B": {"n": 300, "model_acc": 0.8, "strongest_floor": 0.7, "twin_acc": 0.3}}
    out = agg(rows)
    assert out["model_acc"] == 0.75 and out["strongest_floor"] == 0.65 and out["twin_acc"] == 0.25
    assert out["comparators_complete"] is True and out["n_dims_ci_sep_over_floor"] == 1


def test_aggregate_no_comparator_at_all_is_none():
    agg = _agg_fn()
    out = agg({"A": {"n": 10, "model_acc": 0.5, "strongest_floor": None, "twin_acc": None}})
    assert out["strongest_floor"] is None and out["twin_acc"] is None and out["n_with_floor"] == 0


def main():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = 0
    for fn in fns:
        try:
            fn(); print("  [PASS]", fn.__name__)
        except Exception as e:
            fails += 1; print("  [FAIL]", fn.__name__, "--", e)
    print("[witness] %d/%d PASS" % (len(fns) - fails, len(fns)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
