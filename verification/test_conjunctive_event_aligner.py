"""Scaffold-free witness for `the_reader_conflates_similar_events_needs_a_soft_and_conjunctive_grounded_aligner`.

Recomputes the HEADLINE claims FROM SOURCE (imports the cells + the reused organ; uses the already-built rich-event
cache, no re-parse). Each check can fail. Run:
    .venv/Scripts/python.exe verification/test_conjunctive_event_aligner.py

The claims (and how this problem REFINED the brief):
  W1  the reasoning read-out is REUSED UNCHANGED: hdlab.transitive_ordering answers an UN-STATED transitive pair.
  W2  the conjunctive code SEPARATES get_in from get_out (the criterial confusion) where a verb-only identity
      collapses them -- the mechanism.
  W3  THE LEVER is the criterial-feature ROLE-STRUCTURED conjunction: on a real sample, dropping the PATH/2nd-arg
      slots COLLAPSES particle-sibling alignment (ablation), and binding fillers to the WRONG roles destroys it.
  W4  the brief's SOFT-AND PRODUCT is NOT the lever: the uniform geometric-mean product does NOT beat the additive
      sum on the same real sample (the combination rule is secondary; the FEATURE SET is the lever).
  W5  the path/particle must be DISCRETE: raw grounded cosine(in,out) is high (antonyms are grounded-similar), the
      discrete kernel is 0 -- a cosine cannot separate the criterial spatial opposite.
  W6  conjunctive event-TYPE granularity separates get_in/get_out where the verb-only incumbent collapses them.
  W7  end-to-end DIRECTION: on a real sample, conjunctive granularity beats the verb-only incumbent (the p6 collapse).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import torch  # noqa: E402
torch.set_num_threads(1)

import experiments.exp_conjunctive_event_aligner_probe_v1 as P  # noqa: E402
import experiments.exp_conjunctive_aligner_end_to_end_mcscript_v1 as X  # noqa: E402
import experiments.exp_situation_model_inference_mcscript_v1 as E  # noqa: E402
import experiments._situation_inference_live as L  # noqa: E402
from hdlab.transitive_ordering import TransitiveOrderingLine  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail), flush=True)
    if not cond:
        FAILS.append(name)


def mini_scen_events(n_scen=12):
    """Build scen->events for a few scenarios from the EXISTING rich cache (no spaCy re-parse)."""
    import json
    cache_path = P.RICH_CACHE
    assert os.path.exists(cache_path), "rich cache missing -- run the probe cell first"
    cache = json.load(open(cache_path, encoding="utf-8"))
    items = E.collect_symmetric(["dev"])
    scen_set = list(dict.fromkeys(it["scenario"] for it in items))[:n_scen]
    train = L.load_mcscript("train")
    by = defaultdict(list)
    for it in train:
        if it["scenario"] in scen_set:
            by[it["scenario"]].append(it["passage"])
    scen_events = {}
    for scen in scen_set:
        evs = []
        for p in sorted(set(by[scen]))[:12]:
            evs.extend(cache.get(P._pid(p), []))
        if evs:
            scen_events[scen] = evs
    return scen_events


def main():
    print("WITNESS: conjunctive event aligner (soft-AND refined -> criterial-feature conjunction is the lever)\n")

    # -- W1: the reused reasoning read-out is UNCHANGED (answers an un-stated transitive pair) --
    gen = torch.Generator().manual_seed(7)
    line = TransitiveOrderingLine(3, 1024, gen, seed=7)
    line.integrate([(0, 1), (1, 2)])                 # wash<fold, fold<dry ; wash<dry is UN-stated
    check("W1_transitive_ordering_reused_unchanged", line.compare(0, 2) == 1,
          "(un-stated wash<dry read off the integrated line = +1)")

    # -- W2: the conjunctive code separates get_in from get_out (verb-only collapses) --
    sa = P._kernel_gated(0.15)
    cue = {"PRED": "get", "PATH": "out", "PATIENT": "shower", "AGENT": "i", "ARG2": None}
    tgt = {"PRED": "get", "PATH": "out", "PATIENT": "shower", "AGENT": "i", "ARG2": None}
    dis = {"PRED": "get", "PATH": "in", "PATIENT": "shower", "AGENT": "i", "ARG2": None}
    check("W2_conjunction_separates_get_out_from_get_in", sa(cue, tgt) > sa(cue, dis),
          "(gated: get_out=%.3f > get_in=%.3f)" % (sa(cue, tgt), sa(cue, dis)))

    # -- build a mini real probe for W3/W4 --
    scen_events = mini_scen_events(14)
    probe = P.build_probe(scen_events, verbose=False)
    sib = [it for it in probe if it["cond"] == "paraphrase" and it["stratum"] == "particle_sibling"]
    check("W3a_mini_probe_has_particle_sibling_items", len(sib) >= 15, "(n=%d)" % len(sib))

    def acc(kernel):
        ok = [P._argmax_correct([kernel(it["cue"], c) for c in it["cands"]], it["gold_idx"]) for it in sib]
        return float(np.mean(ok)) if ok else 0.0

    full = acc(P._kernel_gated(0.15))
    ablated = acc(P._kernel_gated(0.15, use_particle=False, use_arg2=False))
    scrambled = acc(P._kernel_gated(0.15, scramble={"PRED": "PATIENT", "PATIENT": "PRED",
                                                    "PATH": "ARG2", "ARG2": "PATH", "AGENT": "AGENT"}))
    # -- W3: the criterial-feature conjunction + role structure is the lever --
    check("W3b_criterial_feature_ablation_collapses_alignment", full - ablated > 0.10,
          "(full=%.3f  no_particle_no_arg2=%.3f  delta=%.3f)" % (full, ablated, full - ablated))
    check("W3c_role_scramble_destroys_alignment", full - scrambled > 0.30,
          "(correct_roles=%.3f  scrambled_roles=%.3f)" % (full, scrambled))

    # -- W4: the SOFT-AND PRODUCT is NOT the lever (does not beat the additive sum) --
    softand = acc(P._kernel_softand())
    additive = acc(P._kernel_power(1.0))
    check("W4_uniform_product_does_not_beat_additive_sum", softand <= additive + 0.03,
          "(soft-AND product=%.3f  additive sum=%.3f -> the combination rule is secondary; brief refined)"
          % (softand, additive))

    # -- W5: the path/particle must be discrete (a cosine cannot separate the antonym in/out) --
    from hdlab.grounded_similarity import grounded_vector
    vi, vo = grounded_vector("in"), grounded_vector("out")
    raw = float(np.asarray(vi, float) @ np.asarray(vo, float) /
                (np.linalg.norm(np.asarray(vi, float)) * np.linalg.norm(np.asarray(vo, float)) + 1e-9)) \
        if (vi is not None and vo is not None) else 0.0
    check("W5_antonym_needs_discrete_particle", raw > 0.30 and P.psim("in", "out") == 0.0,
          "(raw grounded cos(in,out)=%.3f is HIGH -> cosine cannot separate; discrete psim(in,out)=0)" % raw)

    # -- W6: conjunctive event-TYPE granularity separates get_in/get_out where verb-only collapses --
    ev_in = {"PRED": "get", "PATH": "in", "PATIENT": "shower"}
    ev_out = {"PRED": "get", "PATH": "out", "PATIENT": "shower"}
    check("W6_conjunctive_type_granularity_separates",
          X.type_key(ev_in, "verb") == X.type_key(ev_out, "verb")
          and X.type_key(ev_in, "verb_path") != X.type_key(ev_out, "verb_path"),
          "(verb-only collapses get_in/get_out; verb_path separates them into distinct orderable nodes)")

    # -- W7: end-to-end DIRECTION on a real sample -- conjunctive granularity beats the verb-only incumbent --
    import json
    cache = json.load(open(P.RICH_CACHE, encoding="utf-8"))
    items = E.collect_symmetric(["dev"])[:120]
    scen = {it["scenario"] for it in items}
    sim_by = {id(it): E.sim_pick([L.content_words(c) for c in it["cands"]],
                                 set(L.content_words(it["passage"]))) for it in items}
    sch_verb = X.induce_conjunctive_schema(scen, cache, "verb", train_cap=12)
    sch_conv = X.induce_conjunctive_schema(scen, cache, "verb_path_pat", train_cap=12)
    ker = P._kernel_gated(0.15)
    a_verb = np.mean([r[0] for r in X._score_arm(items, sch_verb, ker, cache, sim_by)])
    a_conv = np.mean([r[0] for r in X._score_arm(items, sch_conv, ker, cache, sim_by)])
    check("W7_conjunctive_granularity_beats_verbonly_incumbent", a_conv >= a_verb + 0.03,
          "(verb-only=%.3f  conjunctive=%.3f  on a %d-item real dev sample)" % (a_verb, a_conv, len(items)))

    # -- W8: the causal-ENABLEMENT edge builder is correct (the ordering-fix mechanism), and its edges are DENSE
    #    (not sparse) -- yet the located result is that it does NOT beat co-occurrence order (that headline number
    #    lives in data/exp_enablement_order_mcscript_v1/metrics.json; here we witness the mechanism + density). --
    import experiments.exp_enablement_order_mcscript_v1 as EN
    flex = EN.force_lex()
    A = {"PRED": "get", "PATH": None, "PATIENT": "cup", "AGENT": "i", "ARG2": None}
    B = {"PRED": "drink", "PATH": None, "PATIENT": "coffee", "AGENT": "i", "ARG2": "cup"}
    en_ok = EN.enables(A, B, flex) and not EN.enables(B, A, flex)
    check("W8_enablement_edge_builder_directed_and_correct", en_ok,
          "(get(cup)->drink(from cup) fires; reverse blocked -- object-availability enablement)")
    # density on a small real sample (enable premises are NOT sparse -- refutes the sparsity worry)
    nodes = EN.build_nodes(scen, cache, train_cap=12)
    dens = np.mean([len(EN.enable_premises(nd)) for nd in list(nodes.values())[:20] if len(nd["idx"]) >= 2])
    check("W8b_enable_premises_are_dense", dens >= 5.0, "(mean enable-edges/scenario=%.1f on a real sample)" % dens)

    print("\n%s (%d checks, %d failed)" % ("ALL PASS" if not FAILS else "FAILED: " + ", ".join(FAILS),
                                           9 + 2, len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
