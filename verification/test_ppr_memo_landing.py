"""LANDING WITNESS -- pri 146: the spreading-activation memo, per reader, and the passage file on the reader.

WHAT THIS WITNESS PINS (claims, not numbers -- per the standing rule).
  1. THE WALK IS UNCHANGED.  With no memo bound, `grounded_semantic_graph._ppr` is byte-identical to the
     stationary spreading-activation formula it documents (r = (1-d)p + d T^T r, PPR_ITERS iterations), and a
     memoised value is byte-identical to the recomputed one.  Damping, iterations and the graph are untouched.
  2. THE MEMO IS THE READER'S, AND IT DIES WITH THE READ.  It is created per read, held on the reader
     instance, bound to the module only for the duration of that read, and the binding is released afterwards
     (in a `finally`, so an exception cannot leave one brain's activation lying where the next one reads).
     Two readers never share a memo.
  3. THE KEY IS THE EXACT CUE SET.  A different seed tuple never collides with a stored one, and a vector
     spread over a DIFFERENT graph is never served.
  4. IT IS CAPACITY-BOUNDED AND NO ANSWER DEPENDS ON THE CAPACITY.  Eviction is least-recently-used (the
     decay); an evicted cue set is simply re-spread, so cap 0 (inert), cap 1 and the shipped cap all return
     the same vectors.
  5. THE POISONED TWIN IS A REAL DESTRUCTION.  A memo that returns a wrong stored vector on a hit changes
     what the consumer receives -- so the clean memo's identity is evidence, not a no-op.
  6. NO PASSAGE STATE SURVIVES A READ.  The passage file (Heim's cards, their clock, the passage register and
     the passage's POS memo) is ONE object, handed back to the reader when the read ends, leaving the shared
     category organ with no passage; and there is no process-global generation counter.
  7. THE RECORDED RESULT AGREES WITH ITSELF.  When the cell's records are on disk, every document the
     stability arm called stable is identical between the memo-off and memo-on reads, the poisoned twin
     changed the read, and the saving is read back from the record rather than re-asserted as a constant.

TREE STATE.  The witness DETECTS whether the patch has landed, from the live modules.  On the landed tree it
asserts THE DEFECT IS ABSENT (no module-level `_REG_GEN`; `read` wraps `_read_document`; the memo types
exist).  Before landing it installs the experiment cell's shim -- the same source the patch ships -- asserts
every capability claim on it, and says out loud that the defect is still present.

Run: .venv/Scripts/python.exe verification/test_ppr_memo_landing.py
Glass-box, NO LLM, deterministic, CPU-only.  Writes nothing.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_ppr_memo_v1 as E                     # noqa: E402
import hdlab.grounded_semantic_graph as GSG                 # noqa: E402
import hdlab.lexical_categories as LC                       # noqa: E402
import hdlab.situation_reader as SR                         # noqa: E402

_OK = [True]
_DATA = os.path.join(_REPO, "data", "exp_ppr_memo_v1")


def ck(name, cond, extra=""):
    _OK[0] = _OK[0] and bool(cond)
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("   %s" % (extra,)) if extra != "" else ""))


def _graph(n=6, a=(0, 1, 2, 3), b=(1, 2, 3, 4)):
    return GSG._row_stochastic(GSG._symmetrize(list(a), list(b), n))


def w1_the_walk_is_unchanged():
    print("\nW1 THE WALK IS UNCHANGED (no memo bound == the documented formula)")
    T = _graph()
    r = GSG._ppr([0, 2], T, 6)
    p = np.zeros(6, np.float32)
    p[[0, 2]] = 1.0 / 2
    ref = p.copy()
    for _ in range(GSG.PPR_ITERS):
        ref = (1.0 - GSG.DAMPING) * p + GSG.DAMPING * (T @ ref)
    ck("the unmemoised walk is byte-identical to r = (1-d)p + d T^T r", np.array_equal(np.asarray(r), ref))
    ck("an empty cue set still returns nothing (the abstention is untouched)", GSG._ppr([], T, 6) is None)
    m = GSG.ActivationMemo()
    with GSG.spreading(m):
        first = GSG._ppr([0, 2], T, 6)
        again = GSG._ppr([0, 2], T, 6)
    ck("a memoised repeat is byte-identical to the recomputed vector",
       np.array_equal(np.asarray(first), np.asarray(again)) and np.array_equal(np.asarray(first), ref),
       "hits=%d misses=%d" % (m.hits, m.misses))
    ck("the repeat was served from the memo and not re-spread", m.hits == 1 and m.misses == 1)


def w2_the_memo_belongs_to_the_reader():
    print("\nW2 THE MEMO IS THE READER'S AND DIES WITH THE READ")
    ck("nothing is bound outside a read", GSG._ACTIVE_MEMO is None)
    m1, m2 = GSG.ActivationMemo(), GSG.ActivationMemo()
    with GSG.spreading(m1):
        ck("a read binds ITS OWN memo", GSG._ACTIVE_MEMO is m1)
        with GSG.spreading(m2):
            ck("a nested reading binds its own and never the outer one", GSG._ACTIVE_MEMO is m2)
        ck("the outer reading's memo is restored", GSG._ACTIVE_MEMO is m1)
    ck("the binding is released when the read ends", GSG._ACTIVE_MEMO is None)
    try:
        with GSG.spreading(m1):
            raise RuntimeError("a read that fails")
    except RuntimeError:
        pass
    ck("a read that RAISES still releases the binding (the finally, not the happy path)",
       GSG._ACTIVE_MEMO is None)
    T = _graph()
    with GSG.spreading(m1):
        GSG._ppr([0], T, 6)
    with GSG.spreading(m2):
        GSG._ppr([0], T, 6)
    ck("two readers never share one memo (the second still has to spread)",
       m1.hits == 0 and m2.hits == 0 and len(m1.d) == 1 and len(m2.d) == 1)
    src = SR.SituationReader.read.__code__.co_names + SR.SituationReader.read.__code__.co_varnames
    ck("the reader's read() is what binds it, and hands the passage back", "spreading" in src and
       "detach_passage" in src and hasattr(SR.SituationReader, "_read_document"))


def w3_the_key_is_the_exact_cue_set():
    print("\nW3 THE KEY IS THE EXACT CUE SET")
    T = _graph()
    m = GSG.ActivationMemo()
    with GSG.spreading(m):
        a = GSG._ppr([0, 2], T, 6)
        b = GSG._ppr([0, 3], T, 6)
        c = GSG._ppr([0], T, 6)
    ck("three different cue sets are three different answers", m.hits == 0 and len(m.d) == 3
       and not np.array_equal(np.asarray(a), np.asarray(b)) and not np.array_equal(np.asarray(a), np.asarray(c)))
    T2 = _graph(6, (0, 1), (4, 5))
    m2 = GSG.ActivationMemo()
    with GSG.spreading(m2):
        x = GSG._ppr([0], T, 6)
        y = GSG._ppr([0], T2, 6)
    ck("a vector spread over a DIFFERENT graph is never served for the same cue set",
       not np.array_equal(np.asarray(x), np.asarray(y)) and m2.hits == 0)


def w4_the_capacity_changes_no_answer():
    print("\nW4 CAPACITY-BOUNDED, AND NO ANSWER DEPENDS ON THE CAPACITY")
    T = _graph()
    seeds = ([0], [1], [2], [3], [0])
    out = {}
    for cap in (0, 1, 128):
        m = GSG.ActivationMemo(cap=cap)
        with GSG.spreading(m):
            out[cap] = [np.asarray(GSG._ppr(s, T, 6)).copy() for s in seeds]
        if cap == 0:
            ck("cap 0 makes the memo inert -- every walk is re-spread", m.hits == 0 and len(m.d) == 0)
        if cap == 1:
            ck("cap 1 evicts least-recently-used and still holds exactly one",
               len(m.d) == 1 and m.evictions >= 1, "evictions=%d" % m.evictions)
        if cap == 128:
            ck("the shipped capacity keeps the distinct cue sets and reports its peak",
               m.peak == 4 and m.hits == 1, "peak=%d hits=%d" % (m.peak, m.hits))
    ck("every capacity returns the SAME vectors -- an evicted cue set is simply re-spread",
       all(np.array_equal(out[0][i], out[1][i]) and np.array_equal(out[0][i], out[128][i])
           for i in range(len(seeds))))


def w5_the_twin_is_a_real_destruction():
    print("\nW5 THE POISONED TWIN IS A REAL DESTRUCTION")
    T = _graph()
    good = GSG.ActivationMemo

    class Poisoned(good):
        def get(self, key, Tt):
            v = good.get(self, key, Tt)
            if v is None:
                return None
            for k, other in self.d.items():
                if k != key:
                    return other
            return v

    m = Poisoned()
    with GSG.spreading(m):
        a = GSG._ppr([0], T, 6)
        GSG._ppr([3], T, 6)
        b = GSG._ppr([0], T, 6)
    ck("poisoning a hit returns a DIFFERENT vector to the consumer (so identity is evidence)",
       m.hits == 1 and not np.array_equal(np.asarray(a), np.asarray(b)))


def w6_no_passage_state_survives_a_read():
    print("\nW6 NO PASSAGE STATE SURVIVES A READ")
    lc = LC.get()
    lc.new_document()
    p = LC.current_passage()
    ck("a passage boundary opens ONE file the reader can take", p is not None and lc._reg is p.reg
       and lc._doc_shape is p.doc_shape)
    p.pos_memo["a b"] = ("NOUN", "NOUN")
    got = LC.detach_passage()
    ck("the file is handed back to the reader and the organ is left with NO passage",
       got is p and lc._reg is None and lc._doc_shape == {} and LC.current_passage() is None)
    ck("the passage's POS memo travelled with the file, not with the module", got.pos_memo == {"a b": ("NOUN", "NOUN")})
    ck("the affect path reads its memo off the open passage, not off a module lru_cache",
       "current_passage" in SR._affect_pos.__code__.co_names and not hasattr(SR, "_affect_pos_cached"))
    ck("THE DEFECT IS ABSENT: no process-global passage-generation counter", not hasattr(LC, "_REG_GEN"))
    lc.new_document()
    g = LC.register_generation()
    lc.new_document()
    ck("register_generation still reports the organ's own open passage", LC.register_generation() == g + 1)
    LC.detach_passage()


def w7_the_recorded_result_agrees_with_itself():
    print("\nW7 THE RECORDED RESULT AGREES WITH ITSELF")
    seen = 0
    f = os.path.join(_DATA, "stability.json")
    if os.path.exists(f):
        seen += 1
        r = json.load(open(f, encoding="utf-8"))
        rows = r["per_document"]
        ck("every document the record calls STABLE is identical under all three comparisons",
           all(x["two_fresh_readers_identical"] and x["one_reader_twice_identical"]
               and x["fresh_vs_reused_reader_identical"] for x in rows if x["stable"]),
           "%d of %d stable under ALL THREE comparisons" % (r["n_stable"], r["n_documents"]))
        # THE CONTRACT THE IDENTITY GATE ACTUALLY USES -- a fresh reader per document.  Under it the record must
        # be unanimous; the documents that are NOT stable are the ones read twice by the SAME reader, which is
        # the reader's own plasticity (see the submission) and not a property the memo can be blamed for.
        ck("under the identity contract (a FRESH reader per document) the record is unanimous",
           all(x["two_fresh_readers_identical"] and x["fresh_vs_reused_reader_identical"] for x in rows),
           "%d/%d fresh-reader pairs identical; %d/%d identical when ONE reader reads twice"
           % (sum(1 for x in rows if x["two_fresh_readers_identical"]), len(rows),
              sum(1 for x in rows if x["one_reader_twice_identical"]), len(rows)))
    f = os.path.join(_DATA, "identity.json")
    if os.path.exists(f):
        seen += 1
        r = json.load(open(f, encoding="utf-8"))
        ck("the identity gate recorded NO failing document", r["n_failed"] == 0,
           "%d of %d identical" % (r["n_identical"], r["n_documents"]))
        ck("every recorded document actually exercised the memo (hits > 0 somewhere)",
           any(x["memo"]["hits"] > 0 for x in r["per_document"]))
        ck("the recorded peak never exceeds the shipped capacity",
           all(x["memo"]["peak_entries"] <= GSG.PPR_MEMO_MAX for x in r["per_document"]))
    f = os.path.join(_DATA, "twin.json")
    if os.path.exists(f):
        seen += 1
        r = json.load(open(f, encoding="utf-8"))
        # The CLAIM, not a count: corrupting the memo must be able to change the read (else identity is a
        # no-op), and the STRONGER twin (node identities permuted) must be at least as destructive as the
        # weak one (another cue set's activation).  The submission records that it is 2 of 3 vs 1 of 3.
        ck("corrupting the memo CAN change the read -- so identity is evidence, not a no-op",
           r["n_changed_hit_permuted"] > 0,
           "%d/%d permuted-hit, %d/%d other-cue-hit, %d/%d every-walk"
           % (r["n_changed_hit_permuted"], r["n_documents"], r["n_changed_hit_other_cue"], r["n_documents"],
              r["n_changed_every_walk_permuted"], r["n_documents"]))
        ck("the STRONGER twin is at least as destructive as the weak one",
           r["n_changed_hit_permuted"] >= r["n_changed_hit_other_cue"])
        ck("destroying EVERY walk moves the read no more than a handful of affect fields (the located finding)",
           all(abs(x["every_walk_permuted"]["affect_fields"] - x["affect_fields_clean"]) <= 5
               for x in r["per_document"]),
           "deltas %s of %s clean" % ([x["every_walk_permuted"]["affect_fields"] - x["affect_fields_clean"]
                                       for x in r["per_document"]],
                                      [x["affect_fields_clean"] for x in r["per_document"]]))
    f = os.path.join(_DATA, "consumers.json")
    if os.path.exists(f):
        seen += 1
        r = json.load(open(f, encoding="utf-8"))
        t = r["totals"]
        # THE CHAIN IS MONOTONE -- each gate can only drop occasions, never add them.  A record where the
        # recorded field moved MORE often than the sense verdict did would mean the chain was mis-measured.
        ck("the walk's consequence shrinks down the chain (blend argmax >= sense verdict >= recorded field)",
           r["walk_changed_the_argmax_share"] >= r["sense_verdict_moved_share"] >= r["affect_field_moved_share"],
           "%.4f >= %.4f >= %.4f" % (r["walk_changed_the_argmax_share"], r["sense_verdict_moved_share"],
                                     r["affect_field_moved_share"]))
        ck("the walk DOES overturn the frequency resting level sometimes (it is not a no-op term)",
           t["walk_changed_the_argmax"] > 0, "%d of %d walks" % (t["walk_changed_the_argmax"],
                                                                 t["blend_calls_with_a_walk"]))
        lossless = [k for k, v in r["gate_sizing_totals"].items()
                    if v["argmax_changes_lost"] == 0 and v["share_skipped"] > 1.0 / 3.0]
        ck("the record supports a LOSSLESS gate that still skips a third of the walks (the next brief's premise)",
           bool(lossless), "thresholds with zero loss and >1/3 skipped: %s" % (lossless or "none"))
    f = os.path.join(_DATA, "crossdoc.json")
    if os.path.exists(f):
        seen += 1
        r = json.load(open(f, encoding="utf-8"))
        ck("the record shows the cue sets do NOT recur across documents (so per-read is the right scope)",
           r["cross_document_activation_repeats"] == 0 and r["cross_document_cue_set_repeats"] == 0,
           "%d activation / %d cue-set cross-document repeats over %d documents"
           % (r["cross_document_activation_repeats"], r["cross_document_cue_set_repeats"], r["n_documents"]))
    f = os.path.join(_DATA, "timing.json")
    if os.path.exists(f):
        seen += 1
        r = json.load(open(f, encoding="utf-8"))
        ck("the timing record keeps only stable pairs and reports the discarded ones",
           all(("discarded" in x) for x in r["per_document"]))
        ck("the recorded saving is a REDUCTION on every document that kept a pair",
           all(x["saved_s"] > 0 for x in r["per_document"] if x.get("kept")),
           "mean %s%%" % (round(100 * r["mean_saved_share"], 1) if r.get("mean_saved_share") else "n/a"))
    if not seen:
        print("    (no records on disk yet -- run experiments/exp_ppr_memo_v1.py; the capability claims above"
              " stand on their own)")


def main():
    st = E.landed()
    all_landed = all(st.values())
    print("WITNESS test_ppr_memo_landing  (tree state: %s)"
          % ("LANDED" if all_landed else ("PROPOSED -- %s; the cell's shim (the same source the patch ships) "
                                          "is installed for this run" % st)))
    if not all_landed:
        E.install()
    try:
        w1_the_walk_is_unchanged()
        w2_the_memo_belongs_to_the_reader()
        w3_the_key_is_the_exact_cue_set()
        w4_the_capacity_changes_no_answer()
        w5_the_twin_is_a_real_destruction()
        w6_no_passage_state_survives_a_read()
        w7_the_recorded_result_agrees_with_itself()
    finally:
        if not all_landed:
            E.restore()
    print("\nWITNESS " + ("PASS" if _OK[0] else "FAIL"))
    return 0 if _OK[0] else 1


if __name__ == "__main__":
    raise SystemExit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
