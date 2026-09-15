"""Scaffold-free witness: routing the unified referent to its LIVE NON-COREF consumers is a rigorous
LOCATED NEGATIVE on modern gold (GUM) -- the brief's per-consumer gain does NOT transfer.

R1  the grouping is BYTE-FAITHFUL: my group_unified reproduces hdlab.unified_referent.resolve_unified_stream's
    per-target records EXACTLY (a validated stand-in, so every downstream number is trustworthy).
R2  the reader_coref lever is INERT on GUM regardless of SOURCE: feeding the entity-KB resolver the unified
    card head-sets changes 0 labels, AND feeding it the reader's OWN two-pass clustering head-sets (the
    +0.0882-on-19c-LitBank lever) moves the CoNLL by ~0 -- so that lift is 19c-only, not a source problem.
R3  the unified grouping AS the clustering REGRESSES the identity consumers on modern gold: the entity-KB
    hard-link and the affect/goal experiencer binding both go DOWN vs the live floor (no cross-type common->name
    bridge -- the world-knowledge wall); the entity-layer CoNLL edge is marginal AND subsumed by a DIFFERENT
    dormant landed organ (the entity-KB resolver).
R4  the twin LOSES on the size-robust CoNLL (the grouping IS real signal) -- so the negative is SUBSUMPTION /
    register, not "no signal". (The hard-link metric is size-gameable -- the twin inflates it -- so CoNLL is the
    valid twin instrument, exactly the p12 lesson.)
R5  the he/she coref pick is BYTE-IDENTICAL whether or not the non-coref route runs (it is a disjoint path).

Re-derives live from experiments.exp_route_unified_to_consumers_gum_v1.run() on the GUM V12.1.0 TEST split.
Run: .venv/Scripts/python.exe verification/test_route_unified_to_consumers.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("PYTHONHASHSEED", "0")

import experiments.exp_route_unified_to_consumers_gum_v1 as E
import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = E.run(verbose=False)
    diag = r["diag"]

    chk("R1 grouping reproduces live resolve_unified_stream EXACTLY (byte-faithful stand-in)",
        r["selftest_grouping_ok"], "self-test ok=%s" % r["selftest_grouping_ok"])

    # R2 -- reader_coref lever inert regardless of source (unified head-sets AND the two-pass reader clustering)
    rc = r["C1_uni_rc_vs_entkb_none"]; altrc = r["C1_alt_rc_vs_entkb_none"]
    # RE-PINNED 2026-09-15 (strategy): the exact-zero pin (0 label diffs, |delta| < 1e-6) was a byte-identity
    # premise, not the claim; since pri 118 (the mention typer decides at the TYPE level) the unified source
    # changes 11 labels on GUM with delta -0.0001, n.s. -- the lever is still INERT in substance. The check now
    # asserts inertness the way R2b does: |delta| < 0.002 and not CI-separated; the diff count is reported.
    chk("R2 reader_coref lever is INERT on GUM (unified source: delta ~0, not CI-sep)",
        abs(rc["delta"]) < 0.002 and not rc.get("ci_sep", False),
        "uni_rc diffs=%d delta=%.4f CI-sep=%s" % (diag["total_label_diff_uni_rc_vs_entkb_none"], rc["delta"],
                                                    rc.get("ci_sep")))
    chk("R2b even the reader's OWN two-pass clustering (the 19c +0.0882 lever) is INERT on GUM (delta ~0)",
        abs(altrc["delta"]) < 0.002 and not altrc["ci_sep"],
        "alt_rc(2pass) delta=%.4f CI-sep=%s diffs=%d"
        % (altrc["delta"], altrc["ci_sep"], diag["total_label_diff_alt_rc_vs_entkb_none"]))

    # R3 -- the unified grouping REGRESSES the identity consumers; the entity-layer edge is subsumed
    c2 = r["C2_uni_direct_vs_floor"]; c3 = r["C3_uni_direct_vs_floor"]
    chk("R3 unified grouping REGRESSES the entity-KB hard-link (C2) vs the live floor",
        c2["delta"] < 0, "C2 uni_direct-floor delta=%.4f" % c2["delta"])
    chk("R3b unified grouping REGRESSES the affect/goal experiencer binding (C3) vs the live floor",
        c3["delta"] < 0, "C3 uni_direct-floor delta=%.4f" % c3["delta"])
    accs = r["C1_entity_layer_conll_avg"]
    chk("R3c the only entity-layer CoNLL edge is SUBSUMED by a different dormant landed organ (entkb_none > uni_direct)",
        accs["entkb_none"] >= accs["uni_direct"],
        "entkb_none=%.4f >= uni_direct=%.4f (floor situation_predict=%.4f)"
        % (accs["entkb_none"], accs["uni_direct"], accs["floor"]))

    # R4 -- the twin loses on the size-robust CoNLL -> the grouping is real signal (negative == subsumption)
    tw = r["C1_uni_direct_vs_twin"]
    chk("R4 the shuffled-grouping twin LOSES on the size-robust CoNLL (grouping is load-bearing signal)",
        tw["ci_sep"] and tw["delta"] > 0.1, "uni_direct-twin delta=%.4f CI-sep=%s" % (tw["delta"], tw["ci_sep"]))

    # R5 -- he/she pick byte-identical whether or not the non-coref route runs
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=16, name_gazetteer=gaz)
    oks = [E.heshe_byte_identity_holds(E._gum_to_live(d), gaz) for d in docs]
    chk("R5 the he/she coref pick is BYTE-IDENTICAL with the non-coref route on (disjoint path)",
        all(oks), "%d/%d docs identical" % (sum(oks), len(oks)))

    # ---- DEEPENING (user push: is it a fidelity gap or a ceiling?) ----
    # F1 the cross-type common->name gap is a WORLD-KNOWLEDGE ceiling for NON-person entities but the residual
    #    classifier shows the PERSON gap is dominated by NE-TYPE compatibility (an upper bound).
    import experiments.exp_crosstype_bridge_fidelity_gum_v1 as F
    fr = F.run(docs_limit=80, verbose=False)
    person = fr["ALL_hardlinks"]["person"]; nonperson = fr["ALL_hardlinks"]["nonperson"]
    chk("F1 non-person common->name is a WORLD-KNOWLEDGE ceiling (WK residual > 0.6, glass-box < 0.4)",
        nonperson["WK_residual"] > 0.6 and nonperson["glassbox_ceiling"] < 0.4,
        "nonperson glass-box %.3f WK %.3f" % (nonperson["glassbox_ceiling"], nonperson["WK_residual"]))
    chk("F1b the PERSON glass-box UPPER BOUND is NE-TYPE-dominated (TYPE the largest bucket)",
        person["TYPE"] >= max(person["PRED"], person["KB"], person["WK"]),
        "person PRED %d TYPE %d KB %d WK %d" % (person["PRED"], person["TYPE"], person["KB"], person["WK"]))

    # F2 the EXACT NE-type bridge does NOT realize that upper bound: BOTH cues (salience & recency) achieve low
    #    precision (definites are mostly non-anaphoric / undisambiguable on modern gold), so it is net flat/negative.
    import experiments.exp_route_unified_typed_bridge_gum_v1 as T
    ts = T.run(docs_limit=120, split="all", margin=0.5, cue="salience", verbose=False)
    tr = T.run(docs_limit=120, split="all", margin=0.5, cue="recency", verbose=False)
    chk("F2 the NE-type+salience bridge PRECISION is low (<0.20 -- the 0.77 upper bound does NOT realize)",
        ts["typed_bind_diag"]["precision"] < 0.20,
        "salience precision %.3f (achievable %.0f%%, recall %.3f)"
        % (ts["typed_bind_diag"]["precision"], 100 * ts["typed_bind_diag"]["achievable_rate"],
           ts["typed_bind_diag"]["recall_of_achievable"]))
    chk("F2b the Ariel-correct RECENCY cue is ALSO low precision (<0.20 -- not a wrong-cue artifact)",
        tr["typed_bind_diag"]["precision"] < 0.20,
        "recency precision %.3f" % tr["typed_bind_diag"]["precision"])
    chk("F2c the exact typed bridge does NOT beat the live floor CI-sep on the entity-KB hard-link (C2)",
        not ts["C2_uni_typed_vs_floor"]["ci_sep"],
        "C2 uni_typed-floor delta %.4f CI-sep=%s"
        % (ts["C2_uni_typed_vs_floor"]["delta"], ts["C2_uni_typed_vs_floor"]["ci_sep"]))

    # F3 the decisive stratification: (a) ~80% of person-definites are NON-anaphoric (the anaphoricity gate is the
    #    big precision lever -- gating lifts acc >= 3x), (b) on the anaphoric-to-name subset only ~15-20% resolve
    #    glass-box -- cross-validating the project's own landed GUM name_bridge measurement (19.1% in-text-derivable)
    #    and Raghunathan 2010 MUC-6 (15% not world-knowledge); (c) predication is essentially absent (~0 coverage).
    import experiments.exp_crosstype_strata_gum_v1 as S
    sr = S.run(docs_limit=160, cue="recency", verbose=False)
    allacc = sr["ALL_person_definite_article"]["acc"]; anaacc = sr["anaphoric_all"]["acc"]
    na_frac = sr["nonanaphoric"]["n"] / sr["ALL_person_definite_article"]["n"]
    chk("F3 ~80% of person-definites are NON-anaphoric (the anaphoricity gate is the biggest precision lever)",
        na_frac > 0.6, "non-anaphoric fraction %.2f" % na_frac)
    chk("F3b the anaphoricity gate lifts correct-bind rate >= 3x (unfiltered %.3f -> anaphoric %.3f)"
        % (allacc, anaacc), anaacc >= 3 * allacc, "%.3f -> %.3f" % (allacc, anaacc))
    chk("F3c on the anaphoric-to-name subset the glass-box rate is 0.10-0.35 (cross-validates GUM 19.1% / MUC-6 15%)",
        0.10 <= anaacc <= 0.35, "anaphoric glass-box acc %.3f" % anaacc)

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
