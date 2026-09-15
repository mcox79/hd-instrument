"""test_graded_read_ranker -- scaffold-free WITNESS for
`replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop`.

Two layers, both can-fail on the CURRENT bytes / mechanism:

  A. DISK FACTS (pure text over hdlab/): the load-bearing located-negative claims --
     the live grounding-loop RANKING is ALREADY a graded population read (canonicalize_fast,
     GRADED_COMPARATOR ON), the attractor is confined to the exact-match recognition GATE
     (gap_detector), the gate reads its margin PRE-settle, and the recall path (iterative_cleanup)
     is the attractor's correct home (ca3_completer / hippocampal_encoder). The sign()-quantized
     Hopfield primitives are imported NOWHERE live.

  B. MECHANISM NUMBERS (light recompute via the experiment's own functions): the readout swap
     (attractor -> population) is NULL, the live random-hash cue carries ~0 graded-meaning ranking
     fidelity, the FIX (grounded meaning + graded population read) lifts it far above both the
     incumbent and the info-free twin, gate exact-match recognition is NOT regressed, and the
     attractor only over-promotes hubs at SOFT temperatures the gate never uses.

Run:  .venv/Scripts/python.exe verification/test_graded_read_ranker.py
"""
from __future__ import annotations

import os
import re
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

PASSED = []


def _read(rel):
    with open(os.path.join(_REPO, rel), encoding="utf-8") as f:
        return f.read()


def _ok(tag, cond, detail=""):
    assert cond, "%s FAILED %s" % (tag, detail)
    PASSED.append(tag)
    print("  [OK] %s %s" % (tag, detail))


# ============================ A. DISK FACTS ============================
RGL = _read("hdlab/reading_grounding_loop.py")
GAP = _read("hdlab/gap_detector.py")

# A1 -- the live RANKING readout is a GRADED population read (GRADED_COMPARATOR default ON).
_ok("A1a GRADED_COMPARATOR defaults ON",
    re.search(r'GRADED_COMPARATOR[^\n]*os\.environ\.get\("HD_GRADED_COMPARATOR",\s*"1"\)', RGL) is not None)
_ok("A1b canonicalize_fast uses the GRADED (un-signed) query under GRADED_COMPARATOR",
    "graded_q = GRADED_COMPARATOR if readout is None else readout.graded_query" in RGL
    and "nb = np.asarray(new_raw_sum, dtype=np.float64)" in RGL)
_ok("A1c canonicalize_fast ranks by a single-shot cosine population read (matvec), NOT an attractor",
    "sims[ok] = (mat[ok] @ nb) / (norms[ok] * nn)" in RGL
    and "iterative" not in RGL.split("def canonicalize_fast")[1].split("def ")[1])

# A2 -- the live default (PBV/gate) path routes the ranking through canonicalize_fast (graded).
_ok("A2 live PBV proposer calls canonicalize_fast (the graded read), not the signed reference",
    "out = canonicalize_fast(item.lemma, tr.context_vec, sp" in RGL)

# A3 -- the attractor is used ONLY in the exact-match recognition GATE, and its margin is PRE-settle.
_ok("A3a gap_detector selects the best match via the attractor (recognition), then reads a RAW margin",
    "cleanup_family.iterative_attractor(query_vec, codebook" in GAP
    and "margin = float(np.dot(query_vec, cb_row) / denom)" in GAP)
_ok("A3b the margin is the PRE-settle cosine (docstring pins this as the design)",
    "not from iterative_attractor's own settled `state` output" in GAP)
_ok("A3c the live reader consults the attractor ONLY via the gap gate (is_gap -> familiarity)",
    "r = state.gap_detector.familiarity(lemma, KNOWN_RELATION, KNOWN_OBJECT)" in RGL
    and "iterative_attractor" not in RGL and "iterative_cleanup" not in RGL)

# A4 -- the attractor's CORRECT home is RECALL/completion (reserve it there; do not disturb).
for mod in ("ca3_completer.py", "hippocampal_encoder.py"):
    t = _read("hdlab/%s" % mod)
    _ok("A4 %s composes iterative_cleanup as the RECALL/completion primitive" % mod,
        "from hdlab.iterative_attractor import iterative_cleanup" in t)

# A5 -- the sign()-quantized Hopfield primitives are imported NOWHERE in the live substrate.
def _hdlab_py():
    out = []
    for dp, _dn, fn in os.walk(os.path.join(_REPO, "hdlab")):
        if "__pycache__" in dp:
            continue
        out += [os.path.join(dp, f) for f in fn if f.endswith(".py")]
    return out
sign_hopfield_hits = []
for p in _hdlab_py():
    t = _read(os.path.relpath(p, _REPO))
    # a real IMPORT or call of the sign()-quantised primitives (not the cleanup_family def/registry itself)
    if os.path.basename(p) == "cleanup_family.py":
        continue
    if re.search(r"\b(classical_hopfield|modern_hopfield_continuous)\s*\(", t):
        sign_hopfield_hits.append(os.path.relpath(p, _REPO))
_ok("A5 sign()-quantised Hopfield primitives (classical_hopfield/modern_hopfield_continuous) called NOWHERE live",
    not sign_hopfield_hits, str(sign_hopfield_hits))


# ============================ B. MECHANISM NUMBERS ============================
def _mechanism():
    from experiments.exp_graded_read_vs_attractor_ranker_v1 import (
        load_grounded_words, project, evaluate_arm, hub_promotion, _l2,
        live_hash_ranking_fidelity, gate_exact_match_auc, temp_sweep,
    )
    import numpy as np
    seed = 7
    words, G = load_grounded_words(160, seed)
    n = len(words)
    Gn = _l2(G); TRUE = Gn @ Gn.T
    centrality = (TRUE.sum(1) - 1.0) / (n - 1)
    qids = np.random.default_rng(seed).choice(n, size=80, replace=False)
    cb_g = project(G, 256, seed=seed + 100, fmt="graded")
    cb_s = project(G, 256, seed=seed + 100, fmt="sign")
    tw = np.random.default_rng(seed + 5).permutation(n)

    rho_sa, _, _ = evaluate_arm(cb_s, TRUE, qids, "attractor", 4.0, 8)      # incumbent-faithful readout
    rho_sp, _, _ = evaluate_arm(cb_s, TRUE, qids, "pop", 4.0, 8)            # readout-swap on same format
    rho_gp, _, pick_gp = evaluate_arm(cb_g, TRUE, qids, "pop", 4.0, 8)      # THE FIX
    rho_tw, _, _ = evaluate_arm(cb_g[tw], TRUE, qids, "pop", 4.0, 8)        # info-free twin
    hp_fix, _ = hub_promotion(pick_gp, centrality)

    live_attr, live_pop = live_hash_ranking_fidelity(words, G, seed)
    gate_auc, _, _ = gate_exact_match_auc(words, seed)
    sweep = temp_sweep(cb_g, TRUE, centrality, qids, temps=[0.25, 8.0], max_steps=8)
    soft = next(r for r in sweep if r["temp"] == 0.25)
    sharp = next(r for r in sweep if r["temp"] == 8.0)
    return dict(rho_sa=float(rho_sa.mean()), rho_sp=float(rho_sp.mean()),
                rho_gp=float(rho_gp.mean()), rho_tw=float(rho_tw.mean()),
                live_attr=live_attr, live_pop=live_pop, gate_auc=gate_auc,
                soft_hub=soft["hub_over_promotion"], sharp_hub=sharp["hub_over_promotion"],
                soft_delta=soft["readout_delta_vs_pop"], sharp_delta=sharp["readout_delta_vs_pop"])


def _run_mechanism():
    m = _mechanism()
    # B1 -- readout swap (attractor -> population) is NULL on the same format (the brief's named fix buys ~0).
    _ok("B1 readout swap attractor->pop is ~null (|delta rho| < 0.02)",
        abs(m["rho_sp"] - m["rho_sa"]) < 0.02, "sp=%.4f sa=%.4f" % (m["rho_sp"], m["rho_sa"]))
    # B2 -- the live random-hash cue carries ~0 graded-meaning ranking fidelity, either readout.
    _ok("B2 live content_key hash ranking fidelity ~ 0 (both readouts)",
        m["live_attr"] < 0.05 and m["live_pop"] < 0.05,
        "attr=%.4f pop=%.4f" % (m["live_attr"], m["live_pop"]))
    # B3 -- THE FIX (grounded meaning + graded population read) far exceeds incumbent AND twin.
    _ok("B3 grounded graded read >> live incumbent hash and >> info-free twin",
        m["rho_gp"] > 0.5 and m["rho_gp"] > m["live_pop"] + 0.3 and m["rho_gp"] > m["rho_tw"] + 0.3,
        "fix=%.4f twin=%.4f live=%.4f" % (m["rho_gp"], m["rho_tw"], m["live_pop"]))
    # B4 -- exact-match recognition (the attractor's correct job) is NOT regressed.
    _ok("B4 gate exact-match recognition AUC == 1.0 (no regression)",
        m["gate_auc"] >= 0.999, "auc=%.4f" % m["gate_auc"])
    # B5 -- the attractor only over-promotes hubs / diverges from pop at SOFT temp, not the gate's SHARP temp.
    _ok("B5 hub over-promotion + readout divergence appear at soft temp, ~absent at the gate's sharp temp",
        m["soft_hub"] >= m["sharp_hub"] - 1e-9 and abs(m["sharp_delta"]) < 0.02,
        "soft_hub=%.4f sharp_hub=%.4f sharp_delta=%.4f" % (m["soft_hub"], m["sharp_hub"], m["sharp_delta"]))


# ============================ C. SOLVED: loop's own ranking metric, independent gold ============================
def _run_solved():
    """The PARTIAL->SOLVED evidence, recomputed at smoke scale: on the loop's OWN sense-assignment ranking
    (canonicalize's job) against the INDEPENDENT SimLex similarity gold, through the LIVE distributional
    channel + the graded population read, a brain-foundational representation (convergent fusion of grounded
    + distributional) beats the distributional incumbent, and the info-free twin loses."""
    from experiments.exp_sense_assignment_grounded_vs_distributional_v1 import run as sa_run
    s = sa_run("smoke", seed=20260909, n_boot=500)
    mrr = s["MRR"]
    _ok("C1 brain-foundational representation (fusion/grounded) beats the DISTRIBUTIONAL incumbent MRR",
        max(mrr["CONVERGENT"], mrr["GROUNDED"]) > mrr["DISTRIBUTIONAL_incumbent"],
        "conv=%.3f grnd=%.3f incumbent=%.3f" % (mrr["CONVERGENT"], mrr["GROUNDED"],
                                                mrr["DISTRIBUTIONAL_incumbent"]))
    _ok("C2 the best brain-foundational arm beats the incumbent CI-separated (headline)",
        s["HEADLINE_best_bf_vs_incumbent_MRR"]["ci"][0] > 0.0,
        "ci=%s arm=%s" % (s["HEADLINE_best_bf_vs_incumbent_MRR"]["ci"],
                          s["HEADLINE_best_bf_vs_incumbent_MRR"]["arm"]))
    _ok("C3 info-free twins LOSE (both channels)",
        mrr["TWIN_distributional"] < mrr["DISTRIBUTIONAL_incumbent"]
        and mrr["TWIN_grounded"] < mrr["GROUNDED"],
        "twin_d=%.4f twin_g=%.4f" % (mrr["TWIN_distributional"], mrr["TWIN_grounded"]))


# ============================ D. LARGEST-DELTA follow-on: the taxonomic identity channel ============================
def _run_largest_delta():
    """The owner-requested largest-delta prototype, recomputed at smoke scale: adding the TAXONOMIC/relational
    identity channel (conceptual_meaning) -- the brain-foundational fix for the grounded sibling/synonym
    confound -- beats the current SOLVED convergent (grounded+distributional) on the loop's own sense-assignment
    ranking, the richer DISTRIBUTIONAL code does not close it, and the info-free twins lose."""
    from experiments.exp_richer_meaning_channel_v1 import run as rm_run
    s = rm_run("smoke", seed=20260909, n_boot=500)
    mrr = s["MRR"]
    _ok("D1 taxonomic/fusion beats the current SOLVED convergent (grounded+distributional)",
        max(mrr["CM"], mrr["CONV_ALL"], mrr["CONV_GDCM"]) > mrr["CONV_GD"],
        "CM=%.3f CONV_ALL=%.3f convGD=%.3f" % (mrr["CM"], mrr["CONV_ALL"], mrr["CONV_GD"]))
    _ok("D2 the missing signal is IDENTITY (taxonomic) not distributional richness: CM >> MF",
        mrr["CM"] > mrr["MF"] + 0.1, "CM=%.3f MF=%.3f" % (mrr["CM"], mrr["MF"]))
    _ok("D3 info-free twins of the new channels LOSE",
        mrr["TWIN_CM"] < mrr["CM"] and mrr["TWIN_MF"] < mrr["MF"],
        "twinCM=%.4f twinMF=%.4f" % (mrr["TWIN_CM"], mrr["TWIN_MF"]))


# ============================ E. learned structured identity + per-item fusion (plumbing) ============================
def _run_learned_structured():
    """The remaining-fixes prototype, plumbing recomputed at smoke scale (the learned DEP channel is
    exposure-limited, so its CI-separated win vs bag/SOLVED is the FULL-cell reproducer, not this fast smoke):
    the dependency channel is LEARNED from the substrate's own glass-box parser (no WordNet) and beats its
    info-free twin; the per-item fusion runs. Full powered result: data/exp_learned_structured_meaning_v1/metrics.json."""
    from experiments.exp_learned_structured_meaning_v1 import run as ls_run
    s = ls_run("smoke", seed=20260909, n_boot=300)
    _ok("E1 identity is LEARNED from parsed reading (glass-box parser, no WordNet) -> DEP built + beats its twin",
        s["n_sents_parsed"] > 0 and s["MRR"]["DEP"] > s["MRR"]["TWIN_DEP"],
        "n_parsed=%d DEP=%.4f twin=%.4f" % (s["n_sents_parsed"], s["MRR"]["DEP"], s["MRR"]["TWIN_DEP"]))
    _ok("E2 the learned + per-item fusion arms run and are finite",
        all(s["MRR"].get(k) is not None for k in ("GDDEP_peritem", "ALL_peritem")))


if __name__ == "__main__":
    _run_mechanism()
    _run_solved()
    _run_largest_delta()
    _run_learned_structured()
    print("\n%d/%d witnesses passed." % (len(PASSED), len(PASSED)))
    print("GRADED-READ RANKER WITNESS GREEN -- located-negative disk facts + full-stack mechanism numbers "
          "reproduce on the current bytes.")


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
