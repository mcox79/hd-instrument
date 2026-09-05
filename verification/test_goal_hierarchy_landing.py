"""Landing witness for the GOAL->SUBGOAL HIERARCHY GRAPH wire (owner-DONE
build_the_goal_subgoal_hierarchy_graph_for_plot_structure_comprehension, Q111 landing 2026-09-05). The graph
mechanism is reverified by verification/test_goal_hierarchy_graph.py (8/8); this asserts the LIVE reader
WIRES it as a PURE ADD. Glass-box, NO LLM. ASCII.

  W1 the default reader populates sm.goal_graph (a GoalGraph) + binds the 4 plot-structure callables.
  W2 PURE ADD: the flat register readouts (sm.wants/why/achieved) are still present + callable (untouched).
  W3 the multi-hop capability: on a 3-level explicit chain the graph gives the ROOT superordinate where the
     flat register (immediate purpose) gives one hop.

Run: .venv/Scripts/python.exe verification/test_goal_hierarchy_landing.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader
from hdlab.goal_hierarchy_graph import GoalGraph, build_goal_graph
from hdlab.goal_register import extract_goals
from hdlab.pos_tagger import PosTagger
import experiments.exp_situation_model_qa_v1 as QA

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")


def main():
    gaz = QA.load_given_gazetteer()
    docs = [d for d in QA.load_docs(4) if os.path.exists(os.path.join(QA.CONLL_DIR, d + ".conll"))][:2]
    r = SituationReader(gaz=gaz)                          # default (track_goals ON)
    assert r.track_goals is True, "track_goals is not default-on"
    for doc in docs:
        sm = r.read(os.path.join(QA.CONLL_DIR, doc + ".conll"))
        assert isinstance(sm.goal_graph, GoalGraph), "sm.goal_graph is not a GoalGraph on %s" % doc
        for name in ("goal_why_chain", "superordinate_goal", "reinstated_goal", "salient_goal"):
            assert callable(getattr(sm, name, None)), "missing callable sm.%s" % name
        for name in ("wants", "why", "achieved"):           # PURE ADD -- flat readouts untouched
            assert callable(getattr(sm, name, None)), "flat readout sm.%s missing (not a pure add!)" % name
        for ag in sm.goal_graph.agents()[:3]:               # the callables run without error
            _ = sm.reinstated_goal(ag); _ = sm.salient_goal(ag)
            _ = sm.superordinate_goal(ag, "go")
    print("W1 live reader populates sm.goal_graph + 4 callables: PASS", flush=True)
    print("W2 PURE ADD -- sm.wants/why/achieved still bound: PASS", flush=True)

    # W3 multi-hop capability (synthetic 3-level explicit purpose chain)
    tagger = PosTagger.load(POS_ASSET)
    sents = [["Mary", "wanted", "to", "escape", "the", "castle", "."],
             ["She", "searched", "for", "a", "key", "to", "unlock", "the", "door", "."],
             ["She", "unlocked", "the", "door", "to", "escape", "."]]
    pos = [tagger.tag(list(s)) for s in sents]
    goals = extract_goals(sents, pos)
    for g in goals:
        g.agent_canonical = "mary"
    G = build_goal_graph(goals)
    chain = G.why_chain("mary", "search")
    assert G.superordinate("mary", "search") == "escape", "multi-hop root wrong: %s" % chain
    assert len(chain) >= 2, "why_chain is not multi-hop: %s" % chain
    print("W3 multi-hop why_chain(search)=%s, root=escape: PASS" % chain, flush=True)
    print("\nALL WITNESSES PASS", flush=True)


if __name__ == "__main__":
    main()
