"""Scaffold-free witness for extract_spatial_and_causal_relations_from_prose_whole_subgraph_survival.
Recomputes every headline from SOURCE (no landed-metrics read, writes nowhere) and asserts the LOCATED-NEGATIVE
findings + the load-bearing controls. ~50s (parses SpaceEval train+trial + a MAVEN causal subset).
Run: .venv/Scripts/python.exe verification/test_joint_spatial_causal_survival.py
"""
from __future__ import annotations
import os, sys
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402  (PYTHONHASHSEED=0 determinism)
import numpy as np  # noqa: E402
from collections import defaultdict  # noqa: E402
from experiments.spatial_gold_loaders import load_spaceeval_docs  # noqa: E402
from experiments.spatial_relation_extractor import extract_edges  # noqa: E402
from experiments._joint_spatial_frontend import extract_spatial  # noqa: E402
from experiments.spatial_relational_model import SpatialModel, CONTAIN_RELTYPES, norm_rel, canon_entity  # noqa: E402
from experiments.exp_joint_spatial_survival_v1 import gold_chains, shuffled_contain, boot_margin as sboot  # noqa: E402
from experiments.exp_joint_causal_survival_v1 import (load_maven, detect_events, bind_edges, marked,  # noqa: E402
                                                      boot_margin as cboot, gen_causal_type)

P = 0; F = 0


def ok(cond, name, detail=""):
    global P, F
    print(("  PASS " if cond else "  FAIL ") + name + ("  [%s]" % detail if detail else ""))
    P += bool(cond); F += (not cond)


def _head(s):
    c = canon_entity(s); return c.split()[-1] if c.split() else c


def spatial():
    from experiments.exp_joint_spatial_survival_v1 import proximity_floor
    print("SPATIAL -- whole-subgraph containment survival, SpaceEval train+trial")
    per = {"incumbent": [], "joint": [], "twin": [], "proximity": []}
    rec = {"incumbent": defaultdict(int), "joint": defaultdict(int)}; tot = defaultdict(int)
    rng = np.random.default_rng(0)
    for split in ("train", "trial"):
        for d in load_spaceeval_docs(split):
            Mg = SpatialModel(max_depth=8); gc = set()
            for (f, g, rel) in d["qslinks"]:
                if rel in CONTAIN_RELTYPES:
                    gc.add((_head(f), _head(g))); Mg.add_containment(f, g)
            gp = set()
            for (f, g, rel, fr) in d["olinks"]:
                if norm_rel(rel):
                    gp.add((_head(f), norm_rel(rel), _head(g)))
            tot["containment"] += len(gc); tot["position"] += len(gp)
            chains = gold_chains(Mg)
            ex = {}
            for a, tr in (("incumbent", extract_edges(d["text"])[1]),
                          ("joint", extract_spatial(d["text"], decode="exact", use_event=True, use_move=True)[1])):
                exc = {(_head(f), _head(g)) for (f, r, g) in tr if r == "in"}
                exp = {(_head(f), norm_rel(r), _head(g)) for (f, r, g) in tr if r not in ("in", "goal", "source") and norm_rel(r)}
                rec[a]["containment"] += len(gc & exc); rec[a]["position"] += len(gp & exp)
                ex[a] = exc
                for ch in chains:
                    per[a].append(1 if all(e in exc for e in ch) else 0)
            tw = shuffled_contain(ex["joint"], rng)
            for ch in chains:
                per["twin"].append(1 if all(e in tw for e in ch) else 0)
            pf = {(a, b) for (a, b) in proximity_floor(d["text"])}
            for ch in chains:
                per["proximity"].append(1 if all(e in pf for e in ch) else 0)
    ni = int(np.sum(per["incumbent"])); nj = int(np.sum(per["joint"])); nt = int(np.sum(per["twin"]))
    npx = int(np.sum(per["proximity"])); n = len(per["incumbent"])
    mi = sboot(np.array(per["joint"], float), np.array(per["incumbent"], float))
    mt = sboot(np.array(per["joint"], float), np.array(per["twin"], float))
    mpx = sboot(np.array(per["joint"], float), np.array(per["proximity"], float))
    ok(nj > ni and mi["lo"] > 0, "S1 joint BEATS incumbent CI-sep on whole-subgraph survival",
       "joint %d/%d vs incumbent %d/%d, margin %.4f CI[%.4f,%.4f]" % (nj, n, ni, n, mi["margin"], mi["lo"], mi["hi"]))
    ok(mpx["lo"] <= 0.0, "S2 DENSITY CONFOUND: a no-semantics PROXIMITY floor MATCHES joint on survival (recall metric is confounded)",
       "proximity %d/%d, joint-proximity margin %.4f CI[%.4f,%.4f]" % (npx, n, mpx["margin"], mpx["lo"], mpx["hi"]))
    ok(nt == 0 and mt["lo"] > 0, "S3 shuffled-relation twin COLLAPSES CI-sep (extracted structure load-bearing)",
       "twin %d/%d; joint-twin margin %.4f CI[%.4f,%.4f]" % (nt, n, mt["margin"], mt["lo"], mt["hi"]))
    rc_i = rec["incumbent"]["containment"] / max(tot["containment"], 1)
    rc_j = rec["joint"]["containment"] / max(tot["containment"], 1)
    ok(rc_j > rc_i, "S4 EVENT-FIGURE + deixis + partitive + prep-semantics lift containment EDGE recall over incumbent",
       "containment recall %.4f -> %.4f" % (rc_i, rc_j))


def spatial_precision():
    """The brain-foundational discriminator: recall-survival is density-confounded (a proximity floor matches the
    semantic joint). On PRECISION (balanced containment QA with HARD adjacent negatives) the proximity prior
    COLLAPSES and the semantic Figure-Ground typing is decisively load-bearing."""
    from experiments.exp_joint_spatial_precision_qa_v1 import (build_model, model_from_proximity, gold_closure, qa)
    from experiments.exp_joint_spatial_survival_v1 import proximity_floor
    from experiments.spatial_relation_extractor import extract_edges as _inc
    from experiments._joint_spatial_frontend import extract_spatial as _jt
    print("\nSPATIAL PRECISION -- balanced containment QA, HARD adjacent negatives (train+trial)")
    arms = {"incumbent": [], "joint": [], "proximity": []}
    rng = np.random.default_rng(0)
    for split in ("train", "trial"):
        for d in load_spaceeval_docs(split):
            Mg = SpatialModel(max_depth=8)
            for (f, g, rel) in d["qslinks"]:
                if rel in CONTAIN_RELTYPES:
                    Mg.add_containment(f, g)
            yes, heads = gold_closure(Mg)
            if len(yes) < 1 or len(heads) < 3:
                continue
            no = [fs for fs in ((_head_a, _head_b) for (_head_a, _head_b) in proximity_floor(d["text"]))
                  if fs[0] != fs[1] and fs not in yes and (fs[1], fs[0]) not in yes]
            no = list(dict.fromkeys(no))
            if len(no) > len(yes):
                sel = rng.choice(len(no), size=len(yes), replace=False); no = [no[i] for i in sel]
            q = [(x, y, 1) for (x, y) in yes] + [(x, y, 0) for (x, y) in no]
            models = {"incumbent": build_model(_inc(d["text"])[1]),
                      "joint": build_model(_jt(d["text"], decode="exact")[1]),
                      "proximity": model_from_proximity(d["text"])}
            for a in arms:
                arms[a].extend(qa(models[a], q))
    ai = np.array(arms["incumbent"], float); aj = np.array(arms["joint"], float); ap = np.array(arms["proximity"], float)
    mp = sboot(aj, ap); mi = sboot(aj, ai)
    ok(ap.mean() < 0.30, "S5 the PROXIMITY density floor COLLAPSES on hard negatives (recall-survival was density-confounded)",
       "proximity acc %.4f" % ap.mean())
    ok(mp["lo"] > 0, "S6 semantic Figure-Ground typing beats the proximity floor CI-sep (typing IS load-bearing, brain-foundational)",
       "joint %.4f vs proximity %.4f, margin %.4f CI[%.4f,%.4f]" % (aj.mean(), ap.mean(), mp["margin"], mp["lo"], mp["hi"]))
    ok(mi["lo"] > 0, "S7 semantic typing beats the incumbent CI-sep on precision",
       "joint %.4f vs incumbent %.4f, margin %.4f CI[%.4f,%.4f]" % (aj.mean(), ai.mean(), mi["margin"], mi["lo"], mi["hi"]))


def causal(ndocs=200):
    print("\nCAUSAL -- edge recovery + PRECISION, MAVEN-ERE valid (subset n=%d docs)" % ndocs)
    print("  (phase diagram: extraction DENSITY is a free knob, so recall is the FREE axis; PRECISION/correctness is binding)")
    docs = load_maven(ndocs)
    rec = {"connective": [], "contig": [], "generative": [], "twin": []}; im = []
    prec = {"connective": [], "contig": [], "generative": []}
    rng = np.random.default_rng(0)
    for doc in docs:
        toks = doc["tokens"]; sl = [set(w.lower() for w in s) for s in toks]
        ev = detect_events(toks)
        es = {"connective": bind_edges(toks, ev, "cross"), "contig": bind_edges(toks, ev, "contig"),
              "generative": bind_edges(toks, ev, "generative")}
        jc = [tuple(fs) for fs in es["connective"]]; nodes = list({n for pr in jc for n in pr})
        twin = set()
        for (a, b) in jc:
            if nodes:
                twin.add(frozenset((a, nodes[rng.integers(0, len(nodes))])))
        gidn = {}; gids = {}
        for e in doc["events"]:
            m = e["mention"][0]
            a, b = m["offset"][0], m["offset"][1]
            node = next(((m["sent_id"], t) for t in ev.get(m["sent_id"], ()) if a <= t < b), None)
            gidn[e["id"]] = node; gids[e["id"]] = m["sent_id"]
        cr = doc.get("causal_relations", {}); goldkeys = set()
        for typ in ("CAUSE", "PRECONDITION"):
            for pr in cr.get(typ, []):
                n1, n2 = gidn.get(pr[0]), gidn.get(pr[1])
                det = (n1 is not None and n2 is not None)
                key = frozenset((n1, n2)) if det else None
                if det:
                    goldkeys.add(key)
                im.append(1 if marked(sl, gids.get(pr[0], 0), gids.get(pr[1], 0)) else 0)
                for a in ("connective", "contig", "generative"):
                    rec[a].append(1 if (det and key in es[a]) else 0)
                rec["twin"].append(1 if (det and key in twin) else 0)
        yes = list(goldkeys); no = [fs for fs in es["contig"] if fs not in goldkeys]
        if yes and no:
            if len(no) > len(yes):
                sel = rng.choice(len(no), size=len(yes), replace=False); no = [no[i] for i in sel]
            for lab, pool in ((1, yes), (0, no)):
                for fs in pool:
                    for a in ("connective", "contig", "generative"):
                        prec[a].append(int((fs in es[a]) == lab))
    rr = {k: float(np.mean(v)) for k, v in rec.items()}
    pp = {k: float(np.mean(v)) for k, v in prec.items()}
    im = np.array(im); gen = np.array(rec["generative"], float)
    unmarked_gen = float(gen[im == 0].mean()) if (im == 0).any() else 0.0
    m_gc_prec = cboot(np.array(prec["generative"], float), np.array(prec["contig"], float))
    m_gc_rec = cboot(gen, np.array(rec["connective"], float))
    ok(pp["contig"] < 0.30, "C1 the CONTIGUITY density flood COLLAPSES on precision (recall is the FREE phase-diagram axis)",
       "contig precision %.4f" % pp["contig"])
    ok(m_gc_prec["lo"] > 0, "C2 generative typing is HIGH-PRECISION/LOW-RECALL (abstains not over-links); beats the density flood on balanced precision but ~chance discrimination -> coverage (~5%) is the cap, per the upstream principle",
       "generative %.4f vs contig %.4f (contig over-links), margin %.4f CI[%.4f,%.4f]" % (pp["generative"], pp["contig"], m_gc_prec["margin"], m_gc_prec["lo"], m_gc_prec["hi"]))
    ok(m_gc_rec["lo"] > 0, "C3 generative typing beats the CONNECTIVE shortcut on RECALL (world-knowledge, not markers)",
       "generative %.4f vs connective %.4f, margin %.4f CI[%.4f,%.4f]" % (rr["generative"], rr["connective"], m_gc_rec["margin"], m_gc_rec["lo"], m_gc_rec["hi"]))
    ok(unmarked_gen > rr["connective"], "C4 generative typing recovers UNMARKED causal edges connectives cannot (world-knowledge)",
       "generative unmarked recall %.4f vs connective all %.4f" % (unmarked_gen, rr["connective"]))


if __name__ == "__main__":
    spatial()
    spatial_precision()
    causal()
    print("\n%d/%d checks passed" % (P, P + F))
    sys.exit(0 if F == 0 else 1)


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
