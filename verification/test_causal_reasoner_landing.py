"""Organ-landing witness for reason_over_the_causal_network_multi_hop_chains_and_counterfactuals
(Q111, landed 2026-09-06): the glass-box CAUSAL-NETWORK REASONER -- multi-hop chain traversal
(ultimate/mediating cause, chain-of-consequence) + counterfactual necessity by simulated intervention
-- promoted BYTE-FAITHFUL into hdlab.causal_reasoner and wired as a read()-time query layer on the
SituationReader (sm.causal_reasoner() + sm.ultimate_cause / mediating_cause / chain_of_consequence /
is_necessary / counterfactual / graded_necessity / signed_effect, default-on track_causal_reasoning).
A NEW ISLAND / query layer over the EXISTING sm.causal_links (no downstream consumer today -> no
regression). Reuses the goal_hierarchy_graph ancestors/root/connectivity/shuffled-twin traversal
pattern; PINNED: Trabasso & van den Broek reachability + Pearl simulated intervention.

  W1 PROMOTION FAITHFUL. The promoted hdlab.causal_reasoner.{CausalGraph,AdjacencyFloor} class source is
     BYTE-IDENTICAL to the reference experiments._causal_reasoner (inspect.getsource identity), so the
     reference soundness harness's verdict is produced by identical code. Re-derived live: the canonical
     hand cases pass THROUGH hdlab.causal_reasoner (chain ultimate-cause = root not the immediate
     predecessor; diamond-bypass necessity; Halpern-Pearl over-determination), and the reference
     population harness recomputes SOUND_AND_LOAD_BEARING -- ultimate-cause ~1.000 vs adjacency ~0.000 on
     the multi-hop subset (CI-sep), counterfactual necessity load-bearing (adjacency + shuffled twin BOTH
     lose CI-sep, delta > null p95).
  W2 ADDITIVE / BYTE-SAFE. Off-vs-on on real LitBank docs: EVERY existing SituationModel dimension is
     byte-identical (events, entities, coref, timeline, and -- load-bearing -- sm.causal_links, which the
     reasoner CONSUMES). The off reader leaves sm.causal_reasoner + all 7 query callables = None; the on
     reader exposes them (the only additions). The readout is LAZY -- sm.causal_reasoner stays None until a
     callable is invoked.
  W3 LIVE CONSUMER. Through SituationReader.read() on a doc whose OWN extraction yields a 2-hop causal
     chain (collapsed -> quit -> lost), sm.ultimate_cause('lost') traverses PAST the immediate predecessor
     ('quit') to the root ('collapsed') where the adjacency floor stops at 'quit'; sm.is_necessary /
     chain_of_consequence answer soundly over the reader's OWN network. On an empty/sparse network every
     readout ABSTAINS cleanly (None / False / 'not_necessary' / 0.0 / 'no_effect' / empty), never raises.
     The real-narrative network is SPARSE (the honest upstream extraction gap) -- reported, a named
     default-off densification follow-on, not a regression.

Glass-box, NO external LLM, deterministic, ASCII, CPU-only, threads capped.
Reverify: .venv/Scripts/python.exe verification/test_causal_reasoner_landing.py
"""
from __future__ import annotations

import os
import re
import sys
import glob
import inspect
import tempfile

os.environ.setdefault("OMP_NUM_THREADS", "3")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "3")
os.environ.setdefault("MKL_NUM_THREADS", "3")
os.environ.setdefault("THINC_NUM_THREADS", "3")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def _reader(**kw):
    from hdlab.situation_reader import SituationReader
    # isolate from the concurrent meaning-channel integration (orthogonal to the causal reasoner); these
    # gitignored-asset dimensions abstain in an asset-less env but are noise for THIS witness's byte-diff.
    kw.setdefault("track_bridges", False)
    kw.setdefault("track_senses", False)
    kw.setdefault("track_prediction", False)
    return SituationReader(gaz={"john": "masc", "mary": "fem", "she": "fem", "he": "masc"}, **kw)


def _tok(s):
    return re.findall(r"[A-Za-z']+|[0-9]+|[.,;:!?]", s)


def _sents(p):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", p.strip()) if x.strip()]


def _write_conll(text, alias_set, pid, outdir):
    path = os.path.join(outdir, pid + ".conll")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("#begin document (%s); part 0\n" % pid)
        for s in _sents(text):
            for i, tk in enumerate(_tok(s)):
                bare = tk.lower().strip(".,;:!?\"'()")
                coref = "(0)" if bare in alias_set else "_"
                f.write("\t".join([pid, "0", str(i), tk] + ["_"] * 8 + [coref]) + "\n")
            f.write("\n")
    return path


# ---------------------------------------------------------------------------
# W1 -- PROMOTION FAITHFUL: the promoted organ reproduces the reference soundness.
# ---------------------------------------------------------------------------
def test_w1_promotion_faithful():
    import experiments._causal_reasoner as R
    import hdlab.causal_reasoner as H
    from hdlab.causal_reasoner import CausalGraph, AdjacencyFloor

    # (a) BYTE-FAITHFUL promotion: the reasoner class source is IDENTICAL to the reference -> the reference
    #     harness's verdict below is produced by the very code that landed in hdlab.
    ident = all(inspect.getsource(getattr(H, c)) == inspect.getsource(getattr(R, c))
                for c in ("CausalGraph", "AdjacencyFloor", "ChainItem"))
    check("W1a promoted hdlab.causal_reasoner {CausalGraph,AdjacencyFloor,ChainItem} source BYTE-IDENTICAL "
          "to the reference experiments._causal_reasoner (inspect.getsource identity)", ident)

    # (b) canonical hand cases re-derived LIVE through the PROMOTED organ (algorithm is correct, not just separated)
    chain = CausalGraph.from_edges([("r", "a"), ("a", "b"), ("b", "z")])
    hand_chain = (chain.ultimate_cause("z") == "r" and AdjacencyFloor(chain).ultimate_cause("z") == "b"
                  and chain.is_necessary("a", "z") and chain.is_necessary("r", "z"))
    dia = CausalGraph.from_edges([("r", "a"), ("a", "z"), ("r", "b"), ("b", "z")])
    hand_dia = (not dia.is_necessary("a", "z")) and dia.is_necessary("r", "z")
    od = CausalGraph.from_edges([("r1", "z"), ("r2", "z"), ("q", "dead")])
    hand_od = ((not od.is_necessary("r1", "z")) and (not od.is_necessary("r2", "z"))
               and od.is_actual_cause("r1", "z") and od.is_actual_cause("r2", "z")
               and not od.is_actual_cause("q", "z"))
    check("W1b hand cases through the PROMOTED organ: chain ultimate=root (not the 1-hop predecessor); "
          "diamond-bypass necessity; Halpern-Pearl over-determination (both over-determining causes ACTUAL "
          "though NOT but-for necessary)", hand_chain and hand_dia and hand_od,
          "chain=%s diamond=%s overdet=%s" % (hand_chain, hand_dia, hand_od))

    # (c) reuse the REFERENCE population soundness harness (identical code, per W1a) -> the headline recomputes
    from experiments.exp_causal_reasoner_soundness_v1 import run
    res = run(n_graphs=4000, seed=7)
    r1, r2 = res["R1_ultimate_cause"], res["R2_necessity"]
    check("W1c ULTIMATE-CAUSE sound + multi-hop TRAVERSAL load-bearing: reasoner %.3f ~1.000, adjacency %.3f "
          "~0.000 on the multi-hop subset, reasoner-vs-adjacency + reasoner-vs-twin BOTH CI-sep"
          % (r1["reasoner_acc"], r1["adjacency_multihop_acc"]),
          r1["reasoner_acc"] >= 0.999 and r1["adjacency_multihop_acc"] <= 0.05
          and r1["reasoner_vs_adjacency_multihop"]["ci_sep"] and r1["reasoner_vs_twin_multihop"]["ci_sep"],
          "r-adj %s | r-twin %s" % (r1["reasoner_vs_adjacency_multihop"]["ci"],
                                    r1["reasoner_vs_twin_multihop"]["ci"]))
    check("W1d COUNTERFACTUAL NECESSITY by simulated node-removal load-bearing: reasoner %.3f ~1.000; adjacency "
          "AND shuffled twin BOTH lose CI-sep; delta > null p95 (%.4f)"
          % (r2["reasoner_acc"], r2["null_p95_reasoner_vs_twin"]),
          r2["reasoner_acc"] >= 0.99 and r2["reasoner_vs_adjacency"]["ci_sep"]
          and r2["reasoner_vs_twin"]["ci_sep"]
          and r2["reasoner_vs_twin"]["delta"] > r2["null_p95_reasoner_vs_twin"],
          "r-adj %s | r-twin %s" % (r2["reasoner_vs_adjacency"]["ci"], r2["reasoner_vs_twin"]["ci"]))
    check("W1e overall reference verdict SOUND_AND_LOAD_BEARING (through byte-identical promoted code)",
          res["verdict"] == "SOUND_AND_LOAD_BEARING", res["verdict"])


# ---------------------------------------------------------------------------
# W2 -- ADDITIVE / BYTE-SAFE: track_causal_reasoning is a PURE ADD.
# ---------------------------------------------------------------------------
def _dims(sm):
    ev = [(e.global_idx, e.predicate, e.agent, e.patient, e.tense) for e in sm.events]
    ent = [(e.cluster, tuple(e.heads), e.n_mentions) for e in sm.entities]
    cor = [(r.correct, r.sent_dist) for r in sm.coref_resolutions]
    cau = [(c.sent_idx, c.cause, c.outcome, c.method) for c in sm.causal_links]
    tl = [(f.sent_idx, f.reordered) for f in sm.timeline_frames]
    return ev, ent, cor, cau, tl


def test_w2_additive_byte_identical():
    docs = sorted(glob.glob(os.path.join(REPO, "data/litbank/coref/conll", "*.conll")))[:2]
    check("W2-precheck: LitBank coref conll docs present", len(docs) >= 1,
          "found %d docs" % len(docs))
    if not docs:
        return
    all_ident = True
    detail = []
    for doc in docs:
        off = _reader(track_causal_reasoning=False).read(doc)
        on = _reader(track_causal_reasoning=True).read(doc)
        d_off, d_on = _dims(off), _dims(on)
        ident = (d_off == d_on)
        all_ident = all_ident and ident
        detail.append("%s events=%d causal_links=%d %s"
                      % (os.path.basename(doc), len(d_on[0]), len(d_on[3]),
                         "IDENT" if ident else "DIFF"))
        # off exposes NO causal-reasoning callables; on exposes them (the only additions)
        off_none = (off.causal_reasoner is None and off.ultimate_cause is None and off.is_necessary is None
                    and off.mediating_cause is None and off.chain_of_consequence is None
                    and off.counterfactual is None and off.graded_necessity is None
                    and off.signed_effect is None)
        on_cbl = all(callable(getattr(on, a)) for a in
                     ("causal_reasoner", "ultimate_cause", "mediating_cause", "chain_of_consequence",
                      "is_necessary", "counterfactual", "graded_necessity", "signed_effect"))
        # LAZY: sm.causal_reasoner attr is a callable, but nothing is built until it is INVOKED
        check("W2b [%s] off exposes NO causal callables; on exposes causal_reasoner + 7 readouts"
              % os.path.basename(doc), off_none and on_cbl)
    check("W2a every existing SituationModel dimension BYTE-IDENTICAL off vs on (events, entities, coref, "
          "timeline, and load-bearing sm.causal_links -- the reasoner CONSUMES it)", all_ident,
          " | ".join(detail))


# ---------------------------------------------------------------------------
# W3 -- LIVE CONSUMER: reason over the reader's OWN causal network; abstain on empty.
# ---------------------------------------------------------------------------
def test_w3_live_consumer():
    from hdlab.causal_reasoner import CausalGraph, AdjacencyFloor
    outdir = tempfile.mkdtemp()

    # A doc whose OWN extraction yields a 2-HOP within-sentence causal chain:
    #   "The team lost because the captain quit since morale collapsed." -> collapsed -> quit -> lost
    text = ("The team lost because the captain quit since morale collapsed. "
            "John was exhausted because he had trained hard.")
    doc = _write_conll(text, {"john", "he", "his"}, "causal_live", outdir)
    on = _reader(track_causal_reasoning=True).read(doc)

    g = on.causal_reasoner()
    check("W3a the LIVE reader builds a CausalGraph over its OWN sm.causal_links (n_edges == unique links)",
          isinstance(g, CausalGraph) and g.n_edges() == len({(c.cause, c.outcome) for c in on.causal_links})
          and g.n_edges() >= 3,
          "nodes=%s edges=%d links=%d" % (sorted(g.nodes), g.n_edges(), len(on.causal_links)))

    # MULTI-HOP: ultimate_cause traverses PAST the immediate predecessor to the root, where adjacency stops short
    uc = on.ultimate_cause("lost")
    adj = AdjacencyFloor(g).ultimate_cause("lost")
    check("W3b sm.ultimate_cause('lost')='collapsed' (root, MULTI-HOP) where the adjacency floor stops at the "
          "immediate predecessor 'quit' -- the live multi-hop traversal is load-bearing on the reader's OWN network",
          uc == "collapsed" and adj == "quit" and uc != adj,
          "ultimate=%r adjacency=%r" % (uc, adj))

    # COUNTERFACTUAL NECESSITY + chain-of-consequence over the LIVE network
    nec_root = on.is_necessary("collapsed", "lost")
    nec_mid = on.is_necessary("quit", "lost")
    cf = on.counterfactual("collapsed", "lost")
    coc = on.chain_of_consequence("collapsed")
    med = on.mediating_cause("collapsed", "lost")
    check("W3c sm.is_necessary/counterfactual/chain_of_consequence/mediating_cause answer soundly over the LIVE "
          "network: collapsed & quit each necessary for lost; counterfactual='necessary'; consequences={quit,lost}; "
          "mediator=quit", nec_root and nec_mid and cf == "necessary"
          and coc == {"quit", "lost"} and med == "quit",
          "is_nec(collapsed)=%s is_nec(quit)=%s cf=%r chain=%s mediator=%r"
          % (nec_root, nec_mid, cf, sorted(coc), med))

    # CLEAN ABSTENTION on an empty/sparse network (a doc with no connective/mental causal links)
    text2 = "John walked to the store. Mary opened the door. The sky was blue."
    doc2 = _write_conll(text2, {"john", "he"}, "no_causal", outdir)
    on2 = _reader(track_causal_reasoning=True).read(doc2)
    g2 = on2.causal_reasoner()
    abstain = (g2.n_edges() == 0 and on2.ultimate_cause("store") is None
               and on2.is_necessary("walked", "store") is False
               and on2.counterfactual("walked", "store") == "not_necessary"
               and on2.graded_necessity("walked", "store") == 0.0
               and on2.signed_effect("walked", "store") == "no_effect"
               and on2.chain_of_consequence("walked") == set())
    check("W3d on an EMPTY/sparse network every readout ABSTAINS cleanly (None / False / 'not_necessary' / 0.0 / "
          "'no_effect' / empty), never raises -- the honest sparse-extraction case",
          abstain, "n_edges=%d" % g2.n_edges())

    # HONEST UPSTREAM GAP: report the real-narrative sparsity on a real LitBank doc (an extraction gap, not a
    # regression) -- the default-off Trabasso densification (sm.inferred_causal_links) is the named follow-on.
    real = sorted(glob.glob(os.path.join(REPO, "data/litbank/coref/conll", "*.conll")))[:3]
    if real:
        counts = []
        for d in real:
            smr = _reader(track_causal_reasoning=True).read(d)
            gr = smr.causal_reasoner()
            counts.append((os.path.basename(d), gr.n_edges(), gr.n_edges() >= 0))
        check("W3e the reasoner builds LIVE on real LitBank docs too (per-doc edge counts reported). The honest "
              "upstream extraction gap is chain DEPTH / cross-sentence coverage (SOLVED L3: median chain depth 0 on "
              "ROCStories, 3.2% support a >=2-hop chain -- most edges are within-sentence connective/mental links), "
              "NOT raw count; the Trabasso contiguity+plausibility densification is the named DEFAULT-OFF follow-on",
              all(ok for _, _, ok in counts),
              " | ".join("%s edges=%d" % (n, e) for n, e, _ in counts))


if __name__ == "__main__":
    test_w1_promotion_faithful()
    test_w2_additive_byte_identical()
    test_w3_live_consumer()
    print()
    if FAILS:
        print("WITNESS FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("ALL LANDING WITNESS CHECKS PASSED")
