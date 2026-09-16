"""verification/test_object_file_competition.py -- CLAIM-PINNING witnesses for the object-file merge/split
cue competition (priority 136).

Every check below pins a CLAIM -- an invariant, a direction, or a CAN-FIRE control -- never a measured
number (per the standing rule: a witness that pins `n == 2855` or `0.543 <= m <= 0.554` is a defect).

Runs standalone (`.venv/Scripts/python.exe verification/test_object_file_competition.py`) and is
pytest-collectable (every witness is a `test_*` function taking no arguments).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_object_file_competition_v1 as E


def _taught():
    """A tiny hand-counted validity table -- the WITNESS never depends on the built asset."""
    V = E.Validities()
    V.counts["head"]["lemma_match"] = [90.0, 5.0]
    V.counts["head"]["isa"] = [20.0, 30.0]
    V.counts["head"]["mismatch"] = [5.0, 90.0]
    V.counts["head"]["no_head"] = [10.0, 40.0]
    V.counts["phi"]["agree"] = [70.0, 30.0]
    V.counts["phi"]["conflict"] = [2.0, 98.0]
    V.counts["phi"]["unknown"] = [50.0, 50.0]
    V.crit["indefinite"] = [5.0, 95.0]      # Heim: an indefinite introduces a NEW file
    V.crit["definite"] = [80.0, 20.0]       # a definite re-accesses an open one
    V.crit["bare"] = [50.0, 50.0]
    V.recompute()
    return V


def _m(midx, head, span, sent, rank=0, pron=False, gender=None, number="singular"):
    return {"midx": midx, "head": head, "span_toks": span, "is_pronoun": pron, "sent_idx": sent,
            "sent_role_rank": rank, "gender": gender, "name_gender": None, "number": number,
            "cluster": 999, "wtok_start": 0, "gtok_start": 0, "gtok_end": 0}


# ---------------------------------------------------------------------------------------------------
def test_w1_shipped_cannot_separate_two_same_head_referents_and_the_competition_can():
    """W1 THE DEFECT + THE FIX, as a can-fire pair.  Heim's Novelty-Familiarity Condition: a second
    INDEFINITE ("a doctor" after "a doctor") introduces a NEW file; a DEFINITE re-accesses the open one.
    The shipped organ hard-filters on head identity and then ALWAYS MERGES, so it cannot express this."""
    from hdlab.entity_resolver import EntityResolver
    ms = [_m(0, "doctor", ["a", "doctor"], 0), _m(1, "doctor", ["a", "doctor"], 1),
          _m(2, "doctor", ["the", "doctor"], 2)]
    shipped = EntityResolver().cluster(ms, gaz=None)
    assert shipped[0] == shipped[1] == shipped[2], \
        "CAN-FIRE half failed: the shipped organ was expected to merge all three same-head mentions"
    # the shipped organ has NO threshold at all, so NO configuration of it can express the novelty
    # branch; the competition has one, and some operating point on it must.
    got = []
    for tau in (-8.0, -4.0, -2.0, 0.0, 1.0, 2.0, 4.0, 8.0):
        c = E.competition_cluster(ms, None, validities=_taught(), tau=tau)
        got.append((tau, (c[0], c[1], c[2])))
    hit = [t for t, lab in got if lab[0] != lab[1] and lab[1] == lab[2]]
    assert hit, ("no operating point separated the second INDEFINITE while re-accessing on the DEFINITE: %s"
                 % got)


def test_w2_strengths_are_log_odds_and_a_pure_function_of_the_counts():
    """W2 THE MATHEMATICAL FORM (Anderson & Milson 1989 rational analysis): the additive cue weight IS
    log P(value|same) - log P(value|different).  Recomputed from the counts, so the table is never frozen."""
    import math
    V = _taught()
    a = V.alpha
    k = len(E.CUE_VALUES["head"])
    ns = sum(V.counts["head"][v][0] for v in E.CUE_VALUES["head"])
    nd = sum(V.counts["head"][v][1] for v in E.CUE_VALUES["head"])
    want = (math.log((90.0 + a) / (ns + a * k)) - math.log((5.0 + a) / (nd + a * k)))
    assert abs(V.w("head", "lemma_match") - want) < 1e-12, "the strength is not the log-odds of the counts"
    assert V.w("head", "lemma_match") > 0 > V.w("head", "mismatch"), "the log-odds do not order the values"
    # the MISMATCH PENALTY the BF audit names (-P*mismatch, Lewis & Vasishth similarity-based
    # interference) is LEARNED here, not hand-set: a conflicting value gets a NEGATIVE weight.
    assert V.w("phi", "conflict") < 0 < V.w("phi", "agree"), "phi conflict is not penalised"


def test_w3_the_information_free_twin_keeps_the_numbers_and_destroys_the_information():
    """W3 THE CONTROL: the twin is the SAME strengths attached to the WRONG cue values -- identical shape,
    magnitude and coverage, zero information.  (A twin that also changed the magnitudes would confound.)"""
    V = _taught()
    tw = V.permuted(seed=7)
    for c in E.CUES:
        assert sorted(round(x, 9) for x in tw.strength[c].values()) == \
            sorted(round(x, 9) for x in V.strength[c].values()), \
            "the twin changed the multiset of strengths for cue %s" % c
    assert any(tw.strength[c][v] != V.strength[c][v] for c in E.CUES for v in E.CUE_VALUES[c]), \
        "the twin is identical to the real table (the permutation did nothing)"


def test_w4_the_observe_path_moves_a_validity_and_round_trips_through_the_asset():
    """W4 PLASTICITY (owner: nothing frozen).  One confirmed decision moves the strength, and the table
    persists and reloads to the same strengths."""
    import tempfile
    V = E.Validities()
    before = V.w("etype", "licensed")
    for _ in range(40):
        E.observe_file_decision(V, {"etype": "licensed"}, True)
    for _ in range(40):
        E.observe_file_decision(V, {"etype": "blocked"}, False)
    assert V.w("etype", "licensed") > before, "the observe path did not move the validity"
    d = tempfile.mkdtemp()
    p = V.save(os.path.join(d, "t.json"))
    V2 = E.Validities.load(p)
    assert abs(V2.w("etype", "licensed") - V.w("etype", "licensed")) < 1e-12, "the asset does not round-trip"


def test_w5_the_cue_reader_returns_every_declared_cue_in_its_declared_vocabulary_and_reads_no_gold():
    """W5 THE CONTRACT + GOLD-FREEDOM: `file_cues` emits exactly the declared cues with declared values,
    and its source text contains no gold field name (the gold column is the answer key, never an input)."""
    import inspect
    f = E.OFile(0)
    f.update(0, "SUBJECT", "masc", "singular", "doctor", 0, "~ent0", "miller", True)
    cu = E.file_cues(_m(1, "doctor", ["the", "doctor"], 1), f, head="doctor", canon=None, surf="doctor",
                     gender=None, number="singular", definite="definite", is_name=False, sent_idx=1,
                     prev_cb=None, name_link=None, have_spoke=False)
    assert set(cu) == set(E.CUES), "the cue vector is not the declared cue set: %s" % sorted(cu)
    for c, v in cu.items():
        assert v in E.CUE_VALUES[c], "cue %s produced an undeclared value %r" % (c, v)
    src = inspect.getsource(E.file_cues) + inspect.getsource(E.competition_cluster)
    for bad in ("_gold_eid", '"eid"', "gold["):
        assert bad not in src, "the decision path reads a gold field (%s)" % bad


def test_w6_the_retrieval_threshold_is_load_bearing():
    """W6 THE OPERATING POINT (phase diagram): tau IS the ACT-R retrieval threshold.  Pushed high, every
    mention opens its own file (pattern separation); pushed low, everything merges (pattern completion).
    A threshold that changed nothing would mean the competition was not deciding anything."""
    ms = [_m(0, "doctor", ["the", "doctor"], 0), _m(1, "doctor", ["the", "doctor"], 1),
          _m(2, "nurse", ["a", "nurse"], 2)]
    V = _taught()
    hi = E.competition_cluster(ms, None, validities=V, tau=1e9)
    lo = E.competition_cluster(ms, None, validities=V, tau=-1e9)
    assert len(set(hi.values())) == len(ms), "at a very high threshold not every mention opened a new file"
    assert len(set(lo.values())) == 1, "at a very low threshold the files did not all merge"


def test_w7_the_entity_type_spoke_cue_can_fire_and_blocks_the_wrong_type():
    """W7 THE CUE pri 125 NAMED AS MISSING (its `she -> youtube` flood: 'unfixable by filters -- the cue is
    TYPE knowledge').  Gated on the frozen offline asset being present; skipped, loudly, when it is not."""
    from hdlab.typed_spokes import available_entity_type
    if not available_entity_type():
        print("  SKIP W7: the entity-type spoke asset is absent on this tree")
        return
    E._ETYPE_CACHE.clear()
    lic = E._etype_cue("person", {"barack obama"}, True)
    blk = E._etype_cue("person", {"youtube"}, True)
    assert lic == "licensed", "a person-typed NAME did not license a person-headed anaphor (got %r)" % lic
    assert blk == "blocked", ("an organisation-typed NAME did not BLOCK a person-headed anaphor (got %r) "
                             "-- this is exactly pri 125's `she -> youtube` flood" % blk)


def test_w8_the_partition_metric_can_fail_in_both_directions():
    """W8 THE INSTRUMENT: B-cubed must reward the right partition and punish both error directions, so a
    move in it is a real move (an over-merge costs PRECISION, an under-split costs RECALL)."""
    gold = ["a", "a", "b", "b"]
    assert round(E.b3(gold, gold)[2], 6) == 1.0, "B3 of the gold partition is not 1.0"
    over = E.b3(["x", "x", "x", "x"], gold)
    under = E.b3(["p", "q", "r", "s"], gold)
    assert over[0] < 1.0 and abs(over[1] - 1.0) < 1e-9, "an over-merge did not cost precision only"
    assert under[1] < 1.0 and abs(under[0] - 1.0) < 1e-9, "an under-split did not cost recall only"


def test_w9_the_offline_replay_is_the_live_organ():
    """W9 THE FAITHFULNESS ASSERTION the measurement rests on: on a passage read by the LIVE reader,
    re-running the shipped clustering over the captured mentions reproduces `m["cluster"]` exactly, so an
    offline arm is the organ and not a model of it."""
    import hdlab.situation_reader as SR
    from hdlab.entity_resolver import EntityResolver
    from experiments.exp_pronoun_pick_identity_contract_v1 import write_conll
    sents = [["Elizabeth", "opened", "the", "clinic", "."],
             ["The", "founder", "hired", "two", "nurses", "."],
             ["She", "signed", "the", "papers", "."]]
    p = write_conll(sents)
    try:
        rd = SR.SituationReader()
        rd.read(p)
        ms = [dict(m) for m in (rd._coref_mentions or [])]
        base = EntityResolver().cluster(ms, gaz=rd.gaz)
        bad = [m["midx"] for m in ms if not m.get("is_pronoun") and base.get(m["midx"]) is not None
               and -(int(base[m["midx"]]) + 1) != m.get("cluster")]
        # the crosstype bridge may re-file a bound definite, so allow ONLY bridged mentions to differ
        from hdlab.crosstype_live_adapter import build_gold_free_doc
        doc = build_gold_free_doc(ms, base, [list(s) for s in sents], reader=rd)
        binds = EntityResolver().bridge_links(doc, rd.gaz, conf_thr=-3.0) if doc is not None else {}
        bridged = {ms[i]["midx"] for i in binds if 0 <= i < len(ms)}
        assert set(bad) <= bridged, "the offline clustering replay is not the live organ: %s" % bad
    finally:
        try:
            os.unlink(p)
        except OSError:
            pass


def test_w10_installing_the_competition_reaches_the_readers_entity_layer():
    """W10 WIRE, DON'T ISLAND: installing the organ actually changes the reader's OWN entity layer at some
    operating point (it is not an island), and the pronoun record contract pri 131 landed survives at EVERY
    operating point (an entity id or None, never a sentinel)."""
    from experiments.exp_pronoun_pick_identity_contract_v1 import write_conll
    import hdlab.situation_reader as SR
    import hdlab.entity_resolver as ER
    sents = [["A", "doctor", "examined", "the", "patient", "."],
             ["A", "doctor", "arrived", "later", "."],
             ["The", "doctor", "signed", "the", "papers", "."],
             ["She", "left", "the", "clinic", "."]]
    p = write_conll(sents)
    V = _taught()

    def entity_ids(sm):
        return sorted(str(getattr(e, "cluster", None)) for e in (sm.entities or []))

    def contract_ok(sm):
        for r in (sm.coref_resolutions or []):
            if getattr(r, "resolved_entity", "MISSING") == "MISSING":
                return False
        return True
    try:
        sm = SR.SituationReader().read(p)
        base = entity_ids(sm)
        assert contract_ok(sm), "the landed pronoun record contract is gone on the shipped arm"
        changed = []
        saved = ER.EntityResolver.cluster
        try:
            for tau in (-2.0, 0.0, 2.0, 4.0, 8.0):
                def _cl(inner, ms, gaz, _t=tau, **kw):
                    return E.competition_cluster(ms, gaz, validities=V, tau=_t)
                ER.EntityResolver.cluster = _cl
                sm2 = SR.SituationReader().read(p)
                assert contract_ok(sm2), "the pronoun record contract broke at tau=%s" % tau
                if entity_ids(sm2) != base:
                    changed.append(tau)
        finally:
            ER.EntityResolver.cluster = saved
        assert changed, ("installing the competition changed the reader's entity layer at NO operating "
                         "point -- it is islanded")
        sm3 = SR.SituationReader().read(p)
        assert entity_ids(sm3) == base, "the shipped organ was not restored after the arm"
    finally:
        try:
            os.unlink(p)
        except OSError:
            pass


WITNESSES = [v for k, v in sorted(globals().items()) if k.startswith("test_")]


def main():
    ok = 0
    fails = []
    for w in WITNESSES:
        name = w.__name__
        try:
            w()
            ok += 1
            print("  PASS %s" % name)
        except AssertionError as ex:
            fails.append((name, str(ex)))
            print("  FAIL %s -- %s" % (name, ex))
        except Exception as ex:                      # noqa: BLE001 -- a witness that errors is a failure
            fails.append((name, repr(ex)))
            print("  ERROR %s -- %r" % (name, ex))
    print("\n%d/%d witnesses green" % (ok, len(WITNESSES)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
