"""Scaffold-free witness for `the_assembled_reader_is_never_tested_as_a_whole_all_flags_on`.

Recomputes the load-bearing claims FROM SOURCE on real LitBank docs (no landed metrics.json read, no
replay): the assembled reader's dimensions are PARALLEL SILOS -- each re-extracts its own events and
ignores the others -- so (1) turning all flags on reproduces each dimension's ISOLATED output
byte-for-byte (no cross-dimension regression), (2) perturbing the shared event set leaves the other
dimensions BYTE-IDENTICAL (they do not consult it -- the brain-fidelity gap: no shared event token),
(3) the ONE field two flags co-write (sm.events) DOES interact, (4) the one shared-state coupling the
aggregate instrument has -- the QA temporal gold/readout read tense off sm.events -- makes the temporal
question set COLLAPSE fully-on (named interference), (5) the QA readouts never consult the NEW dimension
fields (typed_causal_links / timeline_order), so causation_typed/timeline_register are invisible to the
aggregate, and (6) a corrected readout that consults sm.timeline_order recovers temporal answers the
event-tense readout drops.

Brain frame (PINNED -- research_brain_situation_model_dimension_binding_2026-08-31.md): the brain indexes
ONE bound event token on all dimensions (Zwaan & Radvansky 1998 event-indexing; Franklin et al. 2020 SEM;
Zacks 2007 EST; hippocampal relational binding). N independent re-extraction pipelines is a known
fidelity gap. This witness MEASURES that gap on the live reader.

Run: .venv/Scripts/python.exe verification/test_assembled_reader_all_flags_on.py
ASCII-only, deterministic, CPU-only (spaCy parse for the causation flag -- glass-box, NO LLM).
"""
import hashlib
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_assembled_reader_all_flags_on_v1 as H   # noqa: E402
import experiments.exp_situation_model_qa_v1 as QA             # noqa: E402


def _pick_docs(k):
    docs = []
    for d in QA.load_docs(30):
        if os.path.exists(os.path.join(QA.CONLL_DIR, d + ".conll")):
            docs.append(d)
        if len(docs) >= k:
            break
    return docs


def _agg_sig(readers, docs, gaz, field):
    """Signature of one dimension FIELD across docs, per config (hash of the per-doc signatures)."""
    out = {}
    for name, r in readers.items():
        parts = []
        for d in docs:
            sm = r.read(os.path.join(QA.CONLL_DIR, d + ".conll"))
            parts.append(H.dim_signatures(sm)[field])
        out[name] = hashlib.sha1(repr(parts).encode()).hexdigest()[:16]
    return out


def main():
    gaz = QA.load_given_gazetteer()
    docs = _pick_docs(4)
    assert docs, "no LitBank docs with conll found"
    need = ["default", "TA", "RR", "CT", "TR", "loo_CT", "all_on"]
    readers = {n: H._build_reader(n, gaz) for n in need}
    checks = []

    # (1) NO-REGRESSION: flag-independent dims byte-identical all_on vs default.
    for field in ("entities", "coref", "timeline_frames", "causal_links"):
        s = _agg_sig(readers, docs, gaz, field)
        checks.append((s["all_on"] == s["default"],
                       "[1] no-regression: %-15s all_on == default (byte-identical)" % field))

    # (2) each dimension reproduces its ISOLATED output when all flags are on (byte-exact).
    for field, owner in (("event_set", "TA"), ("timeline_order", "TR"), ("typed_causal", "CT")):
        s = _agg_sig(readers, docs, gaz, field)
        checks.append((s["all_on"] == s[owner],
                       "[2] no-regression: %-15s all_on == %s-alone (isolated output preserved)"
                       % (field, owner)))

    # (3) SILO STRUCTURE: perturbing the event set (default->TA) leaves the other dims byte-identical
    #     -> they do NOT consult sm.events (the brain's shared event token is ABSENT).
    for field in ("timeline_frames", "causal_links"):
        s = _agg_sig(readers, docs, gaz, field)
        checks.append((s["default"] == s["TA"],
                       "[3] SILO: %-15s identical default vs TA (ignores the event set)" % field))
    s_to = _agg_sig(readers, docs, gaz, "timeline_order")
    checks.append((s_to["TR"] == s_to["all_on"],
                   "[3] SILO: timeline_order identical TR vs all_on (ignores TA/RR/CT event changes)"))
    s_tc = _agg_sig(readers, docs, gaz, "typed_causal")
    checks.append((s_tc["CT"] == s_tc["all_on"],
                   "[3] SILO: typed_causal identical CT vs all_on (role_source=parse re-extracts, "
                   "ignores sm.events)"))

    # (4) the ONE co-written field DOES interact: TA's extra events flow into RR's role routing, so the
    #     role signature all_on != RR-alone (a POSITIVE coupling exactly where they share the token).
    s_roles = _agg_sig(readers, docs, gaz, "event_roles")
    checks.append((s_roles["all_on"] != s_roles["RR"],
                   "[4] INTERACTION: event_roles all_on != RR-alone (TA's added events feed RR routing "
                   "-- the one place a shared token exists, they interact)"))

    # (5) NAMED INTERFERENCE: the QA temporal question set is built off sm.events tense; tense_agnostic
    #     stamps a placeholder -> the temporal instrument COLLAPSES fully-on.
    def temporal_q(cfg):
        tot = 0
        for d in docs:
            sm = readers[cfg].read(os.path.join(QA.CONLL_DIR, d + ".conll"))
            tot += len(QA.build_temporal_questions(sm))
        return tot
    tq_def, tq_on = temporal_q("default"), temporal_q("all_on")
    checks.append((tq_def > 0 and tq_on == 0,
                   "[5] INTERFERENCE: QA temporal questions default=%d -> all_on=%d (tense_agnostic "
                   "placeholder tense zeroes the event-tense instrument)" % (tq_def, tq_on)))

    # (6) NON-CONSUMPTION: the QA causal readout reads sm.causal_links (NOT typed_causal_links), so
    #     causation_typed changes NO causal QA answer though it populates a non-empty typed field.
    d0 = docs[0]
    sm_def = readers["default"].read(os.path.join(QA.CONLL_DIR, d0 + ".conll"))
    sm_ct = readers["CT"].read(os.path.join(QA.CONLL_DIR, d0 + ".conll"))
    sents0 = QA._conll_sents(os.path.join(QA.CONLL_DIR, d0 + ".conll"))
    cq = QA.build_causal_questions(sm_def, sents0)
    qa_def, qa_ct = QA.SituationQA(sm_def), QA.SituationQA(sm_ct)
    same_causal = all(qa_def._answer_causal(q) == qa_ct._answer_causal(q) for q in cq)
    typed_nonempty = len(sm_ct.typed_causal_links) > 0
    checks.append((same_causal,
                   "[6] NON-CONSUMPTION: causation_typed populates %d typed links but the QA causal "
                   "readout (reads causal_links) returns IDENTICAL answers -> aggregate is blind to it"
                   % len(sm_ct.typed_causal_links)))

    # (7) THE FIX: read temporal order off sm.timeline_order (the actual dimension field) and recover
    #     answers the broken event-tense readout drops on the all_on model.
    fix = H.corrected_temporal_arm(docs, gaz, {r["doc"]: r for r in __import__("json").load(
        open(QA.WDW_GOLD, encoding="utf-8"))})
    broken_cov = fix["broken_eventtense_readout"]["answered_frac"]
    fixed_cov = fix["fixed_timeline_order_readout"]["answered_frac"]
    checks.append(((fixed_cov or 0) > (broken_cov or 0),
                   "[7] FIX: corrected timeline_order readout answers %.2f of the tense-gold temporal "
                   "questions vs the broken event-tense readout %.2f on the all_on model"
                   % (fixed_cov or 0, broken_cov or 0)))

    # (8) OFF-GENRE GENERALIZATION: the silo structure holds on non-LitBank modern passages.
    import experiments.exp_assembled_reader_integration_diagnostics_v1 as DG
    og = DG.offgenre_silo(gaz)
    checks.append((og["all_silos_hold_offgenre"],
                   "[8] GENERALIZATION: silo structure holds on %d modern non-LitBank passages "
                   "(TA changes events; timeline/causal byte-identical)" % og["n_passages"]))

    # (9) CORRECTED AGGREGATE: once the instrument reads each dimension's CORRECT field, fully-on beats
    #     the default reader (the events win survives; the temporal/causal instrument couplings are removed).
    import experiments.exp_assembled_reader_corrected_aggregate_v1 as CA
    wdw = {r["doc"]: r for r in __import__("json").load(open(QA.WDW_GOLD, encoding="utf-8"))}
    ca = CA.corrected_aggregate(docs, gaz, wdw)
    ev = ca["per_dimension"].get("events", {})
    checks.append((ev.get("fully_on_corrected", 0) > ev.get("baseline", 1),
                   "[9] CORRECTED AGGREGATE: events fully_on_corrected=%s > baseline=%s (the win survives a "
                   "fixed gold); aggregate on=%s vs base=%s"
                   % (ev.get("fully_on_corrected"), ev.get("baseline"),
                      ca["aggregate"]["fully_on_corrected"], ca["aggregate"]["baseline"])))

    # (10) THE SHARED-EVENT-TOKEN ORGAN EXISTS BUT THE READER DOES NOT IMPORT IT (the wiring gap the fix
    #      plan targets: the binding substrate is built -- bind events to entities by role + cause->effect by
    #      index + FHRR decode -- but read() never uses it, so the dimensions cannot bind).
    import hdlab.situation_model_accumulate as SMA
    organ_ok = (hasattr(SMA, "AccumulateRegister") and hasattr(SMA.AccumulateRegister, "add_event")
                and hasattr(SMA, "CausalLinkRegister"))
    import hdlab.situation_reader as SR
    reader_src = open(SR.__file__, encoding="utf-8").read()
    unwired = "situation_model_accumulate" not in reader_src
    checks.append((organ_ok and unwired,
                   "[10] WIRING GAP: the shared-event-token organ (AccumulateRegister.add_event + "
                   "CausalLinkRegister) EXISTS but situation_reader.py never imports it (built=%s, unwired=%s)"
                   % (organ_ok, unwired)))

    # (11) THE BINDING PROBLEM demonstrated on the real FHRR algebra: a bound event token carries the JOINT
    #      (answers same-type disambiguation, binding-shuffle SENSITIVE); a marginal silo is at chance and
    #      shuffle-INVARIANT -- the concrete data-structure reason the silo reader cannot do cross-dim inference.
    import experiments.exp_integrated_shared_event_token_poc_v1 as POC
    poc = POC.run(120)
    dis = poc["same_type_disambiguation_acc"]; flip = poc["binding_shuffle_flip_rate"]
    poc_ok = (dis["integrated_JOINT"] >= 0.95 and 0.35 <= dis["marginal_SILO"] <= 0.65
              and flip["integrated_JOINT"] >= 0.9 and flip["marginal_SILO"] <= 0.05)
    checks.append((poc_ok,
                   "[11] BINDING PROBLEM: JOINT (bound token) disambiguation=%.2f shuffle-flip=%.2f vs MARGINAL "
                   "(silo) disambiguation=%.2f shuffle-flip=%.2f -> silo stores marginals, not the joint"
                   % (dis["integrated_JOINT"], flip["integrated_JOINT"], dis["marginal_SILO"], flip["marginal_SILO"])))

    print("=== witness: assembled reader, ALL FLAGS ON (n_docs=%d) ===" % len(docs))
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg))
        ok_all = ok_all and ok
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
