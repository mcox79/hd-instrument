"""verification/test_information_foraging_organ_witness.py -- scaffold-free witness for the
INFORMATION FORAGING organ and its two supporting pieces, 2026-08-14.

Covers three things that were added on 2026-08-14 and must not silently rot:
  1. `hdlab.information_foraging` -- the Charnov/Constantino-Daw patch-leaving rule, including one
     assertion per numbered silent-failure mode from the design brief.
  2. `hdlab.corpus_registry`     -- the enumerable shelf over data/corpora/ (the thing whose
     ABSENCE was the whole finding of notes/gap_driven_learning_loop_audit_2026-08-13.md).
  3. The STAGE-A blind-spot detector inside `hdlab.reading_grounding_loop.checkpoint` --
     `grounded_by_segment` / `refused_by_segment` on the growth-curve row, plus `segment_skew`.

Runs with tracing=False (nothing here traces). No network. ~30 s.
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def test_information_foraging_selftests_all_pass():
    from hdlab import information_foraging as inf
    res = inf.run_all_selftests()
    assert all(v is True for v in res.values()), res
    # every one of the ten named failure modes has its own assertion
    for i in range(1, 11):
        assert any(k.startswith(f"fm{i}_") for k in res), f"no self-test for failure mode {i}"


def test_corpus_registry_selftests_all_pass_and_shelf_is_bigger_than_four():
    from hdlab import corpus_registry as cr
    res = cr.run_all_selftests()
    assert res["n_entries_on_disk"] >= 30, res["n_entries_on_disk"]
    # THE finding: the loop could address 4 sources; the shelf holds far more.
    assert res["n_readable"] >= 20, res["n_readable"]
    assert "simplewiki" in res["readable"], "the 251 MB corpus that sat unreadable since 2026-07-28"
    assert not cr.enumerate_corpora()[1], "an entry on disk with no registry row"


def test_leave_threshold_moves_with_travel_time():
    """Hayden 2011: a longer travel time must change the leaving behaviour. A fixed threshold is
    a broken organ, so this is the single most diagnostic behavioural check."""
    from hdlab.information_foraging import ForagingConfig, ForagingController

    def residence(travel_tau):
        c = ForagingController(ForagingConfig(travel_step_duration=travel_tau, stochastic=False,
                                              rho_halflife_steps=25.0))
        out = []
        for p in range(12):
            c.enter_patch(f"p{p}")
            g, n = 2.0, 0
            while True:
                c.harvest(g)
                n += 1
                if c.should_leave() or n >= 60:
                    break
                g *= 0.85
            out.append(n)
            c.travel()
        return sum(out[6:]) / 6.0

    assert residence(60.0) > residence(1.0)


def test_travel_updates_rho_with_zero_reward():
    """The single most-forgotten term. Without it, environment-richness sensitivity vanishes."""
    from hdlab.information_foraging import ForagingConfig, ForagingController
    c = ForagingController(ForagingConfig(travel_step_duration=10.0, rho_halflife_steps=20.0))
    c.enter_patch("p")
    for _ in range(6):
        c.harvest(1.0)
    before = c.rho_fast.rho
    c.travel()
    assert c.rho_fast.rho < before
    assert c.rho_fast.n_travel_updates == 1
    assert c.rho_fast.total_time == 6.0 + 10.0


def test_item_count_currency_is_rejected():
    from hdlab.information_foraging import assert_gain_is_not_a_count
    try:
        assert_gain_is_not_a_count([1.0] * 50)
    except AssertionError:
        pass
    else:
        raise AssertionError("a constant gain stream must be rejected")
    assert_gain_is_not_a_count([1.0, 0.4, 0.16])


def test_stage_a_blind_spot_detector_reports_segment_skew():
    """The detector must group refusals AND banked facts by source segment, on a real loop run
    with two deliberately unequal segments. This is the check that would have made the 63.9%
    biology skew loud instead of derivable-but-never-derived."""
    from hdlab.hd_fact_store import HDFactStore
    from hdlab.reading_grounding_loop import (KNOWN_RELATION, MEANING_RELATION, ReadingLoopState,
                                              checkpoint, process_sentence, seed_known_words,
                                              segment_skew)
    store = HDFactStore(n_dim=2048, seed=5,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"}, use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, ["the", "a", "an", "is", "was", "of", "and", "in", "on", "with",
                             "engine", "harvest", "sensor", "field", "manual", "river", "boat",
                             "old", "new", "long", "before", "after", "every", "year"], "seed")
    seg_a = ["The old velmara engine was repaired before the harvest.",
             "A velmara engine is an engine of the old kind.",
             "Every year the velmara engine was repaired before harvest.",
             "The velmara engine was an engine in the field."]
    seg_b = ["The borlune manual is a manual of the river boat.",
             "A borlune manual was long and new.",
             "The borlune manual is a manual with an old boat."]
    p = 0
    for rep in range(5):
        for i, s in enumerate(seg_a):
            process_sentence(state, s, f"a{rep}_{i}", pass_idx=p)
        row_a = checkpoint(state, p, "segment_alpha", schema_thresh=0.10)
        p += 1
        for i, s in enumerate(seg_b):
            process_sentence(state, s, f"b{rep}_{i}", pass_idx=p)
        row_b = checkpoint(state, p, "segment_beta", schema_thresh=0.10)
        p += 1

    assert "grounded_by_segment" in row_b and "refused_by_segment" in row_b, sorted(row_b)
    skew = segment_skew(row_b)
    seen = set(row_b["grounded_by_segment"]) | set(row_b["refused_by_segment"])
    assert seen, "the detector recorded nothing at all"
    assert seen <= {"segment_alpha", "segment_beta"}, seen
    # cumulative counters, and the skew summary must be internally consistent
    assert sum(row_b["refused_by_segment"].values()) == row_b["n_refused_cumulative"]
    assert skew["n_grounded"] == sum(row_b["grounded_by_segment"].values())
    if skew["n_grounded"]:
        assert 0.0 <= skew["dominant_share"] <= 1.0
        assert 0.0 <= skew["normalised_entropy"] <= 1.0


def test_segment_skew_tolerates_a_pre_detector_row():
    """A foundation snapshot written before 2026-08-14 has no such keys; reading it must return
    zeros, never raise."""
    from hdlab.reading_grounding_loop import segment_skew
    s = segment_skew({"pass_idx": 3, "n_refused_cumulative": 7})
    assert s["n_grounded"] == 0 and s["dominant_segment"] is None


def test_retrospective_skew_tool_reproduces_the_biology_share():
    """The retrospective half of Stage A, run against what is actually on disk. The claim on
    record is 'about 64.5% of every definitional term came from one biology segment'; this
    recomputes it from `definitional_facts_v5.jsonl` with a first-segment-wins dedupe."""
    import importlib.util
    path = os.path.join(REPO_ROOT, "tools", "segment_skew_report.py")
    spec = importlib.util.spec_from_file_location("segment_skew_report", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    d = os.path.join(REPO_ROOT, "data", "foundation", "reading_grounding_v5_termboundary")
    if not os.path.isdir(d):
        return    # foundation not present in this checkout; the tool itself is still exercised
    rep = mod.report_foundation(d)
    g = rep["grounded_by_segment_distinct_terms"]
    assert g["dominant"] == "bio_new", g
    assert 0.55 <= g["dominant_share"] <= 0.75, g
    assert g["normalised_entropy"] < 0.80, g


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}", flush=True)
    print(f"ALL {len(fns)} WITNESSES PASSED")
