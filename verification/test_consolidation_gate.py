"""Scaffold-free witness for build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner.

Reproduces, FROM SOURCE (cached offline assets; deterministic; NO external LLM at inference), the load-bearing
claims of the located-negative result -- that a glass-box consolidation gate over reading-derived co-occurrence
CLEANS the raw regression but does NOT reach curated (SyntagNet) quality or beat gloss, with the loss localized:

  SIGNAL-LOSS TRACE (recomputed inline on test-sub, strict doc-disjoint; writes nothing):
    C1  CURATED SyntagNet knowledge RAISES a_s over gloss (knowledge CAN help through this readout)
    C2  ORACLE gold sense-ATTRIBUTION does NOT beat gloss and is coverage-starved (attribution is NOT the leak)
    C3  TOP-K/exemplar readout does NOT beat mean-pool under the diagnostic query (measured; contra hypothesis)

  GATE-CLEANS-RAW (read from the landed read-and-bind + discriminative metrics):
    C4  the consolidation gate BEATS the raw-ungated twin CI-separated (the gate removes noise)
    C5  the RAW-ungated twin REGRESSES below gloss (reproduces the parent's raw-growth regression)
    C6  the best glass-box reading-derived arm still does NOT beat gloss (the located negative)
    C7  MFS-quarantine discrimination beats plain recurrence (the discriminativeness lever is real)

Run: .venv/Scripts/python.exe verification/test_consolidation_gate.py
"""
import os
import sys
import json
from collections import Counter, defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    return ok


def _load(path):
    return json.load(open(path, encoding="ascii"))["result"] if os.path.exists(path) else None


def main():
    C = G1._CACHE
    emb = __import__("pickle").load(open(os.path.join(C, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = __import__("pickle").load(open(os.path.join(C, "sglite_semcorrole_f30.pkl"), "rb"))
    syntag = __import__("pickle").load(open(os.path.join(C, "sglite_syntagnet.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    cand = set()
    for i in test_idx:
        cand.update(recs[i]["tn"])
    seeds_by_syn = {s: G1._seed_words(s, w2i) for s in cand}
    Ctx = G1.precompute_ctx(recs, test_idx, mat, w2i)

    def a_s_mean(assoc):
        return float(G1.score(recs, test_idx, G1.sigs_for(cand, seeds_by_syn, assoc, mat, w2i), Ctx).mean())

    def a_s_topk(assoc):
        mean_sig = G1.sigs_for(cand, seeds_by_syn, assoc, mat, w2i)
        sw = {s: list(seeds_by_syn[s]) + list(assoc.get(s, [])) for s in cand}
        return float(G1.score_topk(recs, test_idx, sw, mean_sig, Ctx, mat, w2i, k=3).mean())

    print("Reproducing signal-loss trace from source (n=%d test-sub) ..." % len(test_idx), flush=True)
    gloss = {s: [] for s in cand}
    curated = {s: [w.lower().split("_")[0] for w in syntag.get(s, [])] for s in cand}
    # oracle attribution from EVEN-doc gold senses
    ocooc = defaultdict(Counter); osel = Counter(); ouni = Counter(); oN = 0
    for i, r in enumerate(recs):
        if doc[i] % 2 == 0:
            ctx = set(x for x in r["ctx"] if x in w2i)
            if ctx:
                ocooc[r["gold"]].update(ctx); osel[r["gold"]] += 1
                for x in ctx:
                    ouni[x] += 1
                oN += 1
    oracle = {}
    for s in cand:
        c = ocooc.get(s, {}); ns = osel.get(s, 0)
        ws = [(w, cnt) for w, cnt in c.items() if cnt >= 2]
        ws.sort(key=lambda x: -x[1])
        oracle[s] = [w for w, _ in ws[:15]]

    g_mean = a_s_mean(gloss); g_topk = a_s_topk(gloss)
    cur_mean = a_s_mean(curated); ora_mean = a_s_mean(oracle)
    print("  gloss mean=%.4f topk=%.4f | curated mean=%.4f | oracle-attr mean=%.4f (assoc/sense=%.2f)"
          % (g_mean, g_topk, cur_mean, ora_mean, float(np.mean([len(oracle[s]) for s in cand]))), flush=True)

    chk("C1 curated SyntagNet knowledge RAISES a_s over gloss (knowledge CAN help)",
        cur_mean > g_mean + 0.02, "curated %.4f vs gloss %.4f" % (cur_mean, g_mean))
    chk("C2 oracle gold ATTRIBUTION does NOT beat gloss (attribution is not the leak; coverage-starved)",
        ora_mean <= g_mean + 0.005, "oracle %.4f vs gloss %.4f" % (ora_mean, g_mean))
    chk("C3 top-k readout does NOT beat mean-pool under the diagnostic query",
        g_topk <= g_mean, "gloss topk %.4f vs mean %.4f" % (g_topk, g_mean))

    # ---- landed metrics: gate-cleans-raw + located negative ----
    rb = _load(os.path.join(_REPO, "data", "exp_consolidation_gate_readbind_v1", "metrics_mean_w0_s2353551_cap15.json"))
    if rb is None:  # fall back to the original tag
        rb = _load(os.path.join(_REPO, "data", "exp_consolidation_gate_readbind_v1", "metrics_s2353551_cap15.json"))
    if rb:
        chk("C4 consolidation gate beats the RAW-ungated twin CI-separated (gate removes noise)",
            rb["CONSOLIDATED_vs_RAW"]["sep"] is True,
            "CONS %.3f vs RAW %.3f" % (rb["a_s_test"]["CONSOLIDATED"], rb["a_s_test"]["RAW"]))
        chk("C5 RAW-ungated twin REGRESSES below gloss (reproduces parent raw-growth regression)",
            rb["RAW_vs_gloss"]["delta"] < 0, "RAW-gloss delta=%.4f" % rb["RAW_vs_gloss"]["delta"])
        chk("C6 best glass-box reading-derived arm does NOT beat gloss CI-sep (the located negative)",
            rb["CONSOLIDATED_vs_gloss"]["sep"] is False,
            "CONS %.3f vs gloss %.3f sep=%s" % (rb["a_s_test"]["CONSOLIDATED"], rb["a_s_test"]["gloss"],
                                                rb["CONSOLIDATED_vs_gloss"]["sep"]))
    else:
        chk("C4-C6 read-and-bind metrics present", False, "missing readbind metrics json")

    dr = _load(os.path.join(_REPO, "data", "exp_consolidation_discriminative_rescore_v1", "metrics_full.json"))
    if dr:
        chk("C7 MFS-quarantine discrimination beats plain recurrence (discriminativeness lever is real)",
            dr["a_s_test"]["DISCRIMINATIVE_mfs_quarantine"] > dr["a_s_test"]["recurrence_only"],
            "discr %.3f vs recur %.3f" % (dr["a_s_test"]["DISCRIMINATIVE_mfs_quarantine"],
                                          dr["a_s_test"]["recurrence_only"]))
    else:
        chk("C7 discriminative metrics present", False, "missing discriminative metrics json")

    # ---- the syntagmatic-tightness ladder converges TO gloss, never above ----
    syn = _load(os.path.join(_REPO, "data", "exp_consolidation_gate_syntactic_v1", "metrics_p1000000.json"))
    if syn:
        chk("C8 real dependency-parsed + discrimination reaches gloss but does NOT cross it (tightness ruled out)",
            syn["a_s_test"]["syntactic_DISCRIMINATIVE"] <= syn["a_s_test"]["gloss"] + 0.003 and
            syn["DISCR_vs_gloss"]["sep"] is False,
            "dep %.3f vs gloss %.3f" % (syn["a_s_test"]["syntactic_DISCRIMINATIVE"], syn["a_s_test"]["gloss"]))

    # ---- grounding: the mechanism is real (separates concrete homonyms) but the 12-dim asset does not cross ----
    from hdlab.grounded_similarity import grounded_vector as _gv
    def _cen(ws):
        vs = [np.asarray(_gv(x)) for x in ws if _gv(x) is not None]
        v = np.mean(vs, 0); return v / (np.linalg.norm(v) + 1e-9)
    rb = _cen(["slope", "land", "water", "river", "edge"]); mb = _cen(["financial", "institution", "money", "loan"])
    cr = _cen(["water", "fish", "boat", "flow"])
    chk("C9 grounding MECHANISM separates senses distribution cannot (river-ctx matches river-bank > money-bank)",
        float(cr @ rb) > float(cr @ mb), "river %.3f vs money %.3f" % (float(cr @ rb), float(cr @ mb)))
    gr = _load(os.path.join(_REPO, "data", "exp_consolidation_grounded_v1", "metrics_full_base.json")) \
        or _load(os.path.join(_REPO, "data", "exp_consolidation_grounded_v1", "metrics_full.json"))
    if gr:
        chk("C10 grounded fusion (12-dim asset) does NOT beat gloss CI-sep (grounding is not the crosser)",
            gr["GROUNDED_fuse_vs_gloss"]["sep"] is False,
            "fuse %.3f vs gloss %.3f" % (gr["a_s_test"]["GROUNDED_fuse"], gr["a_s_test"]["gloss"]))

    inh = _load(os.path.join(_REPO, "data", "exp_consolidation_grounding_inherit_v1", "metrics_full.json"))
    if inh:
        chk("C11 BRAIN-FAITHFUL semantic-inheritance grounding also does NOT cross gloss",
            inh["arms"]["INHERIT"]["vs_gloss"]["sep"] is False,
            "inherit %.3f vs gloss %.3f" % (inh["arms"]["INHERIT"]["a_s"], inh["a_s_gloss"]))

    ind = _load(os.path.join(_REPO, "data", "exp_online_sense_induction_v1", "metrics_full.json"))
    if ind:
        chk("C12 BOTTOM-UP online sense induction (one-pass, no-training) also does NOT cross gloss -- "
            "mechanism-complete: wall is the topical static representation, not any mechanism",
            ind["induced_vs_gloss"]["sep"] is False,
            "induced %.3f vs gloss-key %.3f" % (ind["a_s_induced_key"], ind["a_s_gloss_key"]))

    bfr = _load(os.path.join(_REPO, "data", "exp_brain_faithful_reader_v1", "metrics_full.json"))
    if bfr:
        chk("C13 optimized UPSTREAM foundation (rich atoms) + brain-faithful SELECTION reader BEATS gloss CI-sep "
            "(the maximized glass-box synergy reaches the ceiling)",
            bfr["best_vs_gloss"]["sep"] is True and bfr["arms"].get("L3_rich_oneshot", 0) > bfr["arms"]["L0_gloss_oneshot"],
            "rich %.3f vs gloss %.3f" % (bfr["arms"].get("L3_rich_oneshot", 0), bfr["arms"]["L0_gloss_oneshot"]))
        chk("C13b recurrent attractor SETTLING over-collapses (< gloss) -- one-shot biased-competition is the right settle",
            bfr["arms"].get("L3_rich_SETTLE", 1.0) < bfr["arms"]["L0_gloss_oneshot"],
            "settle %.3f vs gloss %.3f" % (bfr["arms"].get("L3_rich_SETTLE", -1), bfr["arms"]["L0_gloss_oneshot"]))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
