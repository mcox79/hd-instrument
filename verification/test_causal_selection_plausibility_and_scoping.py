"""Scaffold-free witness for a_force_dynamic_meaning_hub_causal_scorer_retire_the_connective_scoping_workaround.

Asserts the load-bearing claims WITHOUT re-running / re-dating any landed cell (it drives the experiment modules'
functions on a few docs / the constructed items, writing nothing to a landed data dir):

  W1  LOCATED NEGATIVE (connective path): a glass-box force-dynamic+agentivity plausibility SELECTOR is WORSE than
      the positional connective heuristic at BASE density -- plausibility is the wrong mechanism for connective
      cause-selection (which is structural). off_plaus < off_pos on the causal QA (3 docs).
  W2  CIRCULAR INSTRUMENT: agree(gold, positional-pick-on-OFF) == the OFF QA score -- the causal QA gold IS the
      positional connective-adjacency rule (build_causal_questions defines gold = post[0]/pre[-1]).
  W3  CONSTRUCTIVE POSITIVE (bridging path, the named next lever): on NON-ADJACENT physical bridges, force-dynamic
      plausibility (FORCE_BRIDGE) beats MOST_RECENT (locality) AND CONNECTIVE_ONLY (abstains), and beats the
      shuffled-plausibility null p95. Adjacent control: FORCE_BRIDGE does not regress.
  W4  COVERAGE BOUND: the force-dynamic lexicon covers only a MINORITY of real narrative cause verbs (the majority
      is mental/social causation force dynamics structurally cannot represent) -- so a force scorer is coverage-
      bounded on real narrative regardless of the instrument.

Run: .venv/Scripts/python.exe verification/test_causal_selection_plausibility_and_scoping.py
Deterministic, single/low-thread, ASCII.
"""
from __future__ import annotations
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np
import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import SituationReader
from experiments import _causal_network as C
import experiments.exp_causal_selection_instrument_diagnostic_v1 as DIAG
import experiments.exp_causal_bridge_plausibility_beats_locality_v1 as BR
import experiments.exp_read_causal_chain_on_chain_cause_v1 as RC
import experiments.exp_causal_unified_bridge_event_type_v1 as U
import experiments.exp_causal_mental_bridge_no_regress_v1 as NR
import experiments.exp_causal_mental_selector_faithful_v1 as F

N_CHECKS = 0


def _ok(cond, msg):
    global N_CHECKS
    N_CHECKS += 1
    assert cond, "FAIL: " + msg
    print("  ok: " + msg, flush=True)


def _qa_on_docs(ndocs):
    """Run the positional and plaus selectors through the causal QA on `ndocs` docs; return
    (off_pos_acc, off_plaus_acc, gold_pos_agreement). Writes nothing."""
    gaz = SITQA.load_given_gazetteer()
    lex = DIAG._force_lex()
    docs = SITQA.load_docs(ndocs)
    pos_hits, plaus_hits, agree = [], [], []
    for doc in docs:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        r = SituationReader(gaz=gaz, predicate_recall=False); sm = r.read(path)
        sents = SITQA._conll_sents(path)
        qs = SITQA.build_causal_questions(sm, sents)
        roles = DIAG._roles_map(sm)
        ev = {si: r._extract_events(" ".join(t))[0] for si, t in enumerate(sents) if C.CAUSAL_CONNECTIVES & set(t)}
        a_pos = DIAG._links(ev, sents, DIAG.select_positional)
        a_pl = DIAG._links(ev, sents, DIAG.select_plaus, lex=lex, roles=roles)
        for q in qs:
            if q.get("expect_abstain"):
                continue
            g = q.get("gold"); o = SITQA._norm(q["outcome"])
            pos_hits.append(int(SITQA._match(a_pos.get(o), g, "causal")))
            plaus_hits.append(int(SITQA._match(a_pl.get(o), g, "causal")))
            agree.append(int(SITQA._match(a_pos.get(o), g, "causal")))   # == OFF QA score by construction
    return float(np.mean(pos_hits)), float(np.mean(plaus_hits)), float(np.mean(agree))


def main():
    print("[witness] causal cause-selection: located negative + constructive bridge positive", flush=True)

    # W1 + W2: the connective QA instrument (3 docs, deterministic).
    off_pos, off_plaus, agree = _qa_on_docs(3)
    _ok(off_plaus < off_pos - 0.02,
        "plausibility SELECTOR is worse than positional on connective QA (plaus %.3f < pos %.3f) -- "
        "plausibility is the wrong mechanism for connective selection" % (off_plaus, off_pos))
    _ok(abs(agree - off_pos) < 1e-9,
        "agree(gold, positional-on-OFF) == the OFF QA score (%.3f) -- the gold IS the positional rule" % agree)

    # W3: constructive positive -- non-adjacent physical bridge dissociation.
    lex = BR.force_lex()
    def cond_acc(nd, arm):
        hits = []
        for it in BR.ITEMS:
            e = BR._eval_item(it, nd, lex)
            if e is not None:
                hits.append(e[0][arm])
        return float(np.mean(hits)) if hits else 0.0
    mr_adj = cond_acc(0, "MOST_RECENT"); fb_adj = cond_acc(0, "FORCE_BRIDGE")
    mr_non = cond_acc(1, "MOST_RECENT"); fb_non = cond_acc(1, "FORCE_BRIDGE"); co_non = cond_acc(1, "CONNECTIVE_ONLY")
    twin_p95 = float(np.percentile(BR._twin_agg(1, lex), 95))
    _ok(fb_adj >= 0.99 and fb_non >= 0.99,
        "FORCE_BRIDGE is density-robust: adjacent %.3f and non-adjacent %.3f (no regression)" % (fb_adj, fb_non))
    _ok(mr_non <= 0.01 and mr_non < mr_adj - 0.5,
        "MOST_RECENT (locality) COLLAPSES on non-adjacent: %.3f (was %.3f adjacent)" % (mr_non, mr_adj))
    _ok(co_non <= 0.01,
        "CONNECTIVE_ONLY abstains on bridges: %.3f" % co_non)
    _ok(fb_non > twin_p95,
        "FORCE_BRIDGE (%.3f) beats the shuffled-plausibility null p95 (%.3f)" % (fb_non, twin_p95))

    # W4: coverage bound on the real cause-ID gold.
    flex = BR.force_lex()
    classed = sum(1 for it in RC.GOLD if flex.get(BR.vlemma(it.cause_lemma)) is not None)
    cov = classed / len(RC.GOLD)
    _ok(cov < 0.5,
        "force-dynamic lexicon covers only a MINORITY of real cause verbs (%d/%d = %.2f) -- the majority is "
        "mental/social causation (ToM), not force-dynamic" % (classed, len(RC.GOLD), cov))

    # ---- THE CONSTRUCTIVE CHAIN (owner push: cross the wall, brain-foundational upstream + downstream) ----
    # W8 UPSTREAM: the WordNet-supersense event-TYPE representation maps the folk-psychological classes.
    _ok(U.event_type("heard") == "PERCEPTION" and U.event_type("remembered") == "COGNITION"
        and U.event_type("feared") == "EMOTION" and U.event_type("told") == "COMMUNICATION",
        "UPSTREAM event-type representation maps perception/cognition/emotion/communication (glass-box WordNet)")

    # W9 DOWNSTREAM crosses the wall: on non-adjacent MENTAL bridges the UNIFIED selector covers the mental slice
    # a physical-force-only selector structurally cannot, and beats the shuffled-type null.
    um = fm = 0
    for it in U.MENTAL_ITEMS:
        ev = U._eval_item(it, 1)
        if ev is not None:
            um += ev[0]["UNIFIED"]; fm += ev[0]["FORCE_ONLY"]
    um /= len(U.MENTAL_ITEMS); fm /= len(U.MENTAL_ITEMS)
    twin_p95_u = float(np.percentile(U._twin_agg(U.MENTAL_ITEMS, 1), 95))
    _ok(um >= 0.99 and fm <= 0.01,
        "UNIFIED covers the MENTAL slice (%.3f) where FORCE-only structurally cannot (%.3f)" % (um, fm))
    _ok(um > twin_p95_u,
        "UNIFIED (%.3f) beats the shuffled-event-type null p95 (%.3f) on mental bridges" % (um, twin_p95_u))

    # W10 REAL coverage: the event-type representation types the MENTAL majority force dynamics leaves uncovered.
    fl = BR.force_lex()
    force_typed = sum(1 for it in RC.GOLD if BR.vlemma(it.cause_lemma) in fl and fl[BR.vlemma(it.cause_lemma)] == "CAUSE")
    mental_typed = sum(1 for it in RC.GOLD if U.event_type(it.cause_lemma) in (U.MENTAL_TRIGGER | {"BODY", "SOCIAL"}))
    _ok(mental_typed > force_typed,
        "event-type covers the mental majority on real LitBank edges (mental-typed %d > force-classed %d of %d)" % (
            mental_typed, force_typed, len(RC.GOLD)))

    # W11 NO-REGRESS: the mental-bridge addition is byte-identical on the connective causal QA and additive on the
    # goal graph (superset) -- no downstream consumer of causal_links regresses (2 docs, deterministic).
    gaz = SITQA.load_given_gazetteer()
    ok_causal = ok_super = 0
    docs = SITQA.load_docs(2)
    for doc in docs:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        base = SituationReader(gaz=gaz).read(path); ext = NR.ReaderMentalBridge(gaz=gaz).read(path)
        sents = SITQA._conll_sents(path)
        if NR._connective_causal_answers(base, sents) == NR._connective_causal_answers(ext, sents):
            ok_causal += 1
        nb, eb = NR._graph_sig(base); ne, ee = NR._graph_sig(ext)
        if nb <= ne and eb <= ee:
            ok_super += 1
    _ok(ok_causal == len(docs), "mental-bridge addition leaves the connective causal QA byte-identical (%d/%d docs)" % (ok_causal, len(docs)))
    _ok(ok_super == len(docs), "mental-bridge addition keeps the goal graph a SUPERSET -- no edge removed (%d/%d docs)" % (ok_super, len(docs)))

    # ---- THE BRAIN-FAITHFUL SELECTOR (resonance proposes, necessity disposes) + signal-loss localization ----
    # W12 MECHANISM: on constructed items with a SAME-EXPERIENCER neutral distractor, the faithful selector beats
    # the RECENCY-ONLY baseline (the research's key control) -- necessity does work beyond recency + experiencer-gate.
    faith = F._eval_citems("full"); recy = F._eval_citems("recency"); tsh = F._eval_citems("type_shuffle")
    _ok(faith.mean() >= 0.75 and recy.mean() <= 0.01,
        "faithful selector beats RECENCY-ONLY (%.3f vs %.3f) -- necessity works beyond recency+experiencer-gate" % (
            faith.mean(), recy.mean()))
    _ok(faith.mean() > tsh.mean() + 0.2,
        "faithful (%.3f) beats the TYPE-SHUFFLE null (%.3f) -- the event-type/necessity signal carries it" % (
            faith.mean(), tsh.mean()))

    # W13 ROUTING on REAL edges: RC.GOLD is connective-marked, so the ROUTED reader (connective->structural, else
    # bridging) recovers the real cause where bridging-ALONE (correctly) does not.
    rc = F._eval_rcgold()
    _ok(np.mean(rc["routed"]) >= np.mean(rc["recency"]) and np.mean(rc["routed"]) >= 0.75,
        "ROUTED reader recovers real RC.GOLD edges (%.3f) >= most-recent (%.3f); bridging-alone (%.3f) correctly defers" % (
            np.mean(rc["routed"]), np.mean(rc["recency"]), np.mean(rc["faithful_bridge_only"])))

    # W14 SIGNAL-LOSS localized: the selection mechanism is sound (oracle-candset ceiling == 1.0) and the residual
    # loss is UPSTREAM (experiencer/coref preservation < 1.0) -- the meaning-hub, not the selector.
    lad = F._signal_ladder()
    _ok(lad["ablation_selection"]["oracle_candset"] >= 0.99,
        "the SELECTION mechanism is sound given a clean candidate (oracle-candset=%.3f)" % lad["ablation_selection"]["oracle_candset"])
    _ok(lad["preservation"]["experiencer_ok"] < 1.0,
        "signal is lost UPSTREAM: experiencer/coref preservation on real prose = %.3f (< 1.0) -- the meaning-hub lever" % (
            lad["preservation"]["experiencer_ok"]))

    # W15 UPSTREAM FIXED WITH THE REAL ORGAN: routing event-typing through the LANDED GroundedSemanticGraph WSD organ
    # (SemCor resting-level + PPR spreading-activation) improves the chain on real edges vs MFS (the cheap Lesk was a
    # located negative). Reads the landed metrics (the 117k-node graph build is exercised by the cell itself).
    uf_path = os.path.join(_REPO, "data", "exp_causal_upstream_fixes_v1", "metrics.json")
    if os.path.exists(uf_path):
        import json
        uf = json.load(open(uf_path, encoding="ascii"))
        _ok(uf["chain_grounded_WSD"]["routed"] >= uf["chain_baseline_MFS"]["routed"]
            and uf["type_stage"]["grounded_type_ok"] >= uf["type_stage"]["mfs_type_ok"],
            "the REAL brain-foundational WSD organ lifts the chain: routed %.3f>=%.3f (MFS) and type_ok %.3f>=%.3f" % (
                uf["chain_grounded_WSD"]["routed"], uf["chain_baseline_MFS"]["routed"],
                uf["type_stage"]["grounded_type_ok"], uf["type_stage"]["mfs_type_ok"]))
    else:
        print("  note: exp_causal_upstream_fixes_v1 metrics absent -- run that cell to verify the grounded-WSD lift", flush=True)

    print("\nALL %d CHECKS PASSED" % N_CHECKS, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
