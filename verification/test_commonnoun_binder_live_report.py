"""verification/test_commonnoun_binder_live_report.py -- scaffold-free witness for
problem: report_the_typed_coref_organ_onto_the_live_reader_common_noun_path_and_measure

Recomputes every headline of exp_commonnoun_binder_live_report_v1 from source on the FULL GUM modern TEST (odd docs,
n=2855 anaphoric common-noun mentions) and asserts:
  W1 FAITHFULNESS: the resolve mirror (bridge='off') == hdlab.commonnoun_binder.situation_predict BYTE-IDENTICAL.
  W2 NO-REGRESS BY CONSTRUCTION: the non-writing bridge arms (person + all) produce byte-identical CLUSTER LABELS to
     base -> sm.entities + the separate reader pronoun stream are byte-unchanged.
  W3 POSITIVE CONTROL: the board-lemma string-identity floor == the URG board floor 0.5412 (identical population).
  W4 PREMISE (live path): the DEPLOYED binder RESOLUTION accuracy trails string-identity (0.4904 < 0.5412).
  W5 REFUTATION (the brief's mechanism): re-porting the two levers onto the deployed binder does NOT beat string-
     identity CI-separated (the generalized non-writing bridge reaches PARITY: CI includes 0).
  W6 REAL LEVER: the generalized non-writing bridge BEATS base CI-sep AND its info-free twin LOSES CI-sep; removing the
     binder's PERSON-GATE (all vs person) is the load-bearing part (CI-sep).
  W7 BINDING IS THE DEFICIT: the URG/typed-coref resolution binding on the SAME live schema BEATS the deployed binder
     binding CI-sep (+~0.058).
  W8 THE FIX: the committed hdlab.typed_coref organ BEATS string-identity CI-sep (+0.0259) on this exact population and
     BEATS the deployed binder CI-sep (+~0.077).
  W9 CONTROLS: NAME no-regress (not a regress); p11's WRITING type-license is a wash-to-negative over base (its live
     cost is the pronoun drag p11 measured, not a resolution gain).

Glass-box, CPU, numpy + nltk-WordNet only, NO external LLM. Recomputes -- writes NOTHING to any landed dir.
Run: .venv/Scripts/python.exe verification/test_commonnoun_binder_live_report.py
"""
from __future__ import annotations
import experiments._hashseed_guard  # noqa: F401  -- MUST be first (byte-reproducible)

import os, sys, random

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_unified_referent_gum_v1 as URG
import hdlab.commonnoun_binder as CN
import experiments.exp_commonnoun_binder_live_report_v1 as X

NB = 2000
SEED = 13


def main():
    gaz, test = X._load(None)                       # FULL GUM modern TEST = odd docs
    dictments = [X.doc_to_binder_mentions(d) for d in test]

    # ---- W1 FAITHFULNESS + W2 NO-REGRESS BY CONSTRUCTION (byte-identical labels) ----
    n_lbl = 0
    for ms in dictments:
        gold = CN.situation_predict(ms, gaz, window=16, headmatch_gate=True)
        base, _ = X.situation_predict_resolve(ms, gaz, bridge="off")
        nwp, _ = X.situation_predict_resolve(ms, gaz, bridge="nowrite", bridge_scope="person")
        nwa, _ = X.situation_predict_resolve(ms, gaz, bridge="nowrite", bridge_scope="all")
        assert base == gold, "W1 FAITHFULNESS FAIL: resolve(off) != hdlab binder"
        assert nwp == gold and nwa == gold, "W2 NO-REGRESS FAIL: a non-writing arm changed cluster labels"
        n_lbl += len(gold)

    # ---- arms (per-doc aggregates), identical population n=2855 ----
    def perdoc(fn):
        return [X.per_doc_agg(fn(ms)[1]) for ms in dictments]

    sid_board = [X.per_doc_agg(X.string_identity_resolve(ms, key="lemma_head")) for ms in dictments]
    base = perdoc(lambda ms: X.situation_predict_resolve(ms, gaz, bridge="off"))
    tlw = perdoc(lambda ms: X.situation_predict_resolve(ms, gaz, bridge="write", bridge_scope="person"))
    brp = perdoc(lambda ms: X.situation_predict_resolve(ms, gaz, bridge="nowrite", bridge_scope="person"))
    bra = perdoc(lambda ms: X.situation_predict_resolve(ms, gaz, bridge="nowrite", bridge_scope="all"))
    brat = perdoc(lambda ms: X.situation_predict_resolve(ms, gaz, bridge="nowrite", bridge_scope="all",
                                                          twin=True, rng=random.Random(99)))
    urgb = perdoc(lambda ms: X.urg_binding_resolve(ms, gaz, bridge="nowrite"))
    urgbt = perdoc(lambda ms: X.urg_binding_resolve(ms, gaz, bridge="nowrite", twin=True, rng=random.Random(99)))
    urgnb = perdoc(lambda ms: X.urg_binding_resolve(ms, gaz, bridge="off"))
    _tcr = X.TC.TypedCorefResolver(bridge=True, bridge_write=False, type_comparator="typed_spokes")
    organ = [X.per_doc_agg(_tcr.resolve_doc(d)) for d in test]
    livesch = X._liveschema_perdoc(test)                                   # FULL fix on the EXACT live dict schema
    livesch_twin = X._liveschema_perdoc(test, twin=True, rng=random.Random(99))
    livesch_oracle = X._liveschema_perdoc(test, bridge_oracle=True)        # ceiling of a PERFECT type comparator
    livesch_encyc = X._liveschema_perdoc(test, encyc=True)                 # + ENCYCLOPEDIC route (WN instance-of)
    livesch_encyc_twin = X._liveschema_perdoc(test, encyc=True, twin=True, rng=random.Random(99))
    livesch_reason = X._liveschema_perdoc(test, reason=True)               # + REASONING route (situation-model role-fit)
    livesch_all = X._liveschema_perdoc(test, encyc=True, reason=True)      # ALL brain-foundational routes combined
    livesch_encyc_reach = X._liveschema_perdoc(test, encyc=True, encyc_mode="person_reach")  # occupation-KB reconciliation

    def a(arm):
        return X.acc(arm, "common")

    def boot(base_arm, arm, mt="common"):
        return URG._paired_boot(base_arm, arm, mt, NB, SEED)   # (delta, lo, hi, hw): arm - base_arm

    sid_v, n = a(sid_board)
    base_v, _ = a(base); brp_v, _ = a(brp); bra_v, _ = a(bra); brat_v, _ = a(brat)
    urgb_v, _ = a(urgb); urgnb_v, _ = a(urgnb); urgbt_v, _ = a(urgbt); tlw_v, _ = a(tlw); organ_v, _ = a(organ)
    livesch_v, _ = a(livesch); oracle_v, _ = a(livesch_oracle); encyc_v, _ = a(livesch_encyc)
    reason_v, _ = a(livesch_reason); all_v, _ = a(livesch_all)

    checks = []

    def chk(name, cond, detail):
        checks.append((name, bool(cond), detail))

    # W3 positive control: board-lemma string-identity == the URG board floor 0.5412
    chk("W3 positive control: string-identity floor == URG board 0.5412 (n=%d)" % n,
        abs(sid_v - 0.5412) < 1e-4 and n == 2855, "floor=%.4f n=%d" % (sid_v, n))

    # W4 premise: deployed binder trails string-identity
    d, lo, hi, _ = boot(sid_board, base)
    chk("W4 premise: deployed binder RESOLUTION trails string-identity on the live path",
        base_v < sid_v and hi < 0, "binder_base=%.4f floor=%.4f delta=%+.4f ci=[%.4f,%.4f]" % (base_v, sid_v, d, lo, hi))

    # W5 refutation: generalized non-writing bridge does NOT beat the floor CI-sep (parity)
    d, lo, hi, _ = boot(sid_board, bra)
    chk("W5 refutation: binder+levers does NOT beat string-identity CI-sep (parity, CI includes 0)",
        not (lo > 0), "bridge_all=%.4f floor=%.4f delta=%+.4f ci=[%.4f,%.4f]" % (bra_v, sid_v, d, lo, hi))

    # W6a real lever: generalized bridge beats base CI-sep
    d, lo, hi, _ = boot(base, bra)
    chk("W6a lever: generalized non-writing bridge BEATS base CI-sep",
        lo > 0, "delta=%+.4f ci=[%.4f,%.4f]" % (d, lo, hi))
    # W6b twin loses CI-sep
    d, lo, hi, _ = boot(brat, bra)
    chk("W6b twin: info-free twin LOSES CI-sep (type signal load-bearing)",
        lo > 0, "bridge_all=%.4f twin=%.4f delta=%+.4f ci=[%.4f,%.4f]" % (bra_v, brat_v, d, lo, hi))
    # W6c person-gate removal is the lever
    d, lo, hi, _ = boot(brp, bra)
    chk("W6c person-gate: removing the binder person-gate (all vs person) is load-bearing CI-sep",
        lo > 0, "person=%.4f all=%.4f delta=%+.4f ci=[%.4f,%.4f]" % (brp_v, bra_v, d, lo, hi))

    # W7 binding is the deficit: URG binding on the same schema beats the binder binding CI-sep
    d, lo, hi, _ = boot(base, urgb)
    chk("W7 binding deficit: URG resolution binding on the SAME live schema BEATS the deployed binder binding CI-sep",
        lo > 0, "urg_binding=%.4f binder_base=%.4f delta=%+.4f ci=[%.4f,%.4f]" % (urgb_v, base_v, d, lo, hi))
    # W7b the bridge is a lever under the URG binding too, twin loses
    _, lo1, _, _ = boot(urgnb, urgb)
    _, lo2, _, _ = boot(urgbt, urgb)
    chk("W7b under URG binding: bridge beats no-bridge CI-sep AND twin loses CI-sep",
        lo1 > 0 and lo2 > 0, "urg_bridge=%.4f urg_nobridge=%.4f urg_twin=%.4f" % (urgb_v, urgnb_v, urgbt_v))

    # W8 the fix: the committed typed_coref organ BEATS the floor CI-sep on this population + beats the binder CI-sep
    d, lo, hi, _ = boot(sid_board, organ)
    chk("W8 fix: committed hdlab.typed_coref organ BEATS string-identity CI-sep on the live population",
        lo > 0, "organ=%.4f floor=%.4f delta=%+.4f ci=[%.4f,%.4f]" % (organ_v, sid_v, d, lo, hi))
    d2, lo2, hi2, _ = boot(base, organ)
    chk("W8b fix delta: committed organ BEATS the deployed binder CI-sep",
        lo2 > 0, "organ=%.4f binder_base=%.4f delta=%+.4f ci=[%.4f,%.4f]" % (organ_v, base_v, d2, lo2, hi2))

    # W10 THE FULL FIX ON THE EXACT LIVE DICT SCHEMA beats string-identity CI-sep + recovers the organ
    d, lo, hi, _ = boot(sid_board, livesch)
    chk("W10 full fix on the LIVE dict schema BEATS string-identity CI-sep (recovers the organ on the exact schema)",
        lo > 0 and abs(livesch_v - organ_v) < 0.005,
        "liveschema=%.4f organ=%.4f floor=%.4f delta=%+.4f ci=[%.4f,%.4f]" % (livesch_v, organ_v, sid_v, d, lo, hi))
    # W11 the appos/name seeds close the reduced->full gap (reduced urg_binding only reached parity), + beats binder + twin loses
    _, lo1, _, _ = boot(urgb, livesch)
    _, lo2, _, _ = boot(base, livesch)
    _, lo3, _, _ = boot(livesch_twin, livesch)
    chk("W11 full-seed live-schema fix BEATS the reduced port CI-sep (seeds close the gap), beats binder CI-sep, twin loses",
        lo1 > 0 and lo2 > 0 and lo3 > 0,
        "liveschema=%.4f reduced=%.4f binder=%.4f (all deltas CI-sep>0)" % (livesch_v, urgb_v, base_v))

    # W9 controls: NAME no-regress; writing type-license is a wash-to-negative over base
    dn, lon, hin, _ = boot(base, bra, "name")
    chk("W9a NAME no-regress (generalized bridge vs base): not a regress",
        hin >= 0, "delta=%+.4f ci=[%.4f,%.4f]" % (dn, lon, hin))
    dw, low, hiw, _ = boot(base, tlw)
    chk("W9b p11 WRITING type-license is a wash-to-negative over base on resolution (its live cost is the pronoun drag)",
        not (low > 0), "write=%.4f base=%.4f delta=%+.4f ci=[%.4f,%.4f]" % (tlw_v, base_v, dw, low, hiw))

    # W13 WORLD-KNOWLEDGE HEADROOM: a PERFECT type comparator (oracle: gold-coreferent = perfect type/world knowledge)
    # lifts resolution far above both the floor and our WordNet-seeded fix -> the type comparator is the dominant lever
    # and the residual is the ENCYCLOPEDIC/SCHEMA knowledge the C5(WordNet) comparator misses (the built-but-unshipped
    # C8 DBpedia instance-of KB + a scenario/schema store).
    d, lo, hi, _ = boot(livesch, livesch_oracle)
    d2, lo2, hi2, _ = boot(sid_board, livesch_oracle)
    chk("W13 world-knowledge headroom: a perfect type comparator BEATS the WordNet fix CI-sep (+~0.18) and the floor (+~0.21)",
        lo > 0 and lo2 > 0,
        "oracle=%.4f fix=%.4f floor=%.4f | oracle-fix=%+.4f oracle-floor=%+.4f" % (oracle_v, livesch_v, sid_v, d, d2))

    # W14 ENCYCLOPEDIC ROUTE (WordNet instance-of, offline lower-bound of the DBpedia C8 spoke): a real, additive,
    # twin-controlled lift over the taxonomic-only fix -> the encyclopedic route works (the STRONG version = the C8
    # asset, sibling-proven +0.0955 on the name slice). Labels byte-identical (non-writing) -> no-regress by construction.
    d, lo, hi, _ = boot(livesch, livesch_encyc)
    _, lot, _, _ = boot(livesch_encyc_twin, livesch_encyc)
    chk("W14 encyclopedic route (WN instance-of + person-typing) BEATS the taxonomic-only fix CI-sep AND its twin loses (additive lower bound)",
        lo > 0 and lot > 0,
        "encyc=%.4f fix=%.4f delta=%+.4f ci=[%.4f,%.4f] (strong version=DBpedia C8, sibling +0.0955 name-slice)" % (
            encyc_v, livesch_v, d, lo, hi))

    # W15 REASONING route (situation-model role-fit) is a LOCATED NEGATIVE on GUM common-noun resolution (brain-
    # foundational mechanism, negligible addressable slice ~6/2855 -> not CI-sep), while the COMBINED brain-complete
    # comparator (taxonomic + encyclopedic + role-fit) beats the taxonomic-only fix CI-sep (encyclopedic-dominated).
    dR, loR, hiR, _ = boot(livesch, livesch_reason)
    dA, loA, hiA, _ = boot(livesch, livesch_all)
    chk("W15 reasoning route = located NEGATIVE (role-fit ~wash, CI incl 0) AND all-routes-combined beats the fix CI-sep",
        (not (loR > 0)) and loA > 0,
        "reason=%.4f (d=%+.4f ci=[%.4f,%.4f]) all=%.4f (d=%+.4f ci=[%.4f,%.4f]) fix=%.4f" % (
            reason_v, dR, loR, hiR, all_v, dA, loA, hiA, livesch_v))

    # W16 OCCUPATION-KB RECONCILIATION (strategy 2026-09-08: the occupation/entity-type axis is a located negative).
    # The COARSE person-typing route (person-name -> person-CATEGORY anaphor) is a real TYPE constraint on the HONEST
    # de-leaked floor: it beats the 'reach a recent person' control (person-name licenses ANY anaphor) CI-sep -> the
    # anaphor-type match is load-bearing, not just reach. This is DISTINCT from the specific occupation-KB (coverage-bounded);
    # handed off to the world-knowledge problem to reconcile, not claimed as this problem's headline.
    d, lo, hi, _ = boot(livesch_encyc_reach, livesch_encyc)
    chk("W16 occupation-KB reconciliation: coarse person-typing's anaphor-TYPE match beats person-REACH CI-sep (real type constraint, honest floor)",
        lo > 0, "encyc=%.4f reach=%.4f delta=%+.4f ci=[%.4f,%.4f]" % (encyc_v, a(livesch_encyc_reach)[0], d, lo, hi))

    # W12 OOD ROBUSTNESS (GENTLE, out-of-domain): the defect + the fix GENERALIZE off GUM (direction + magnitude;
    # n=275 is underpowered for CI-separation, so this is a DIRECTION check, honestly not a CI-sep claim).
    _, gentle = X._load_gentle()
    if gentle:
        gsid = [X.per_doc_agg(X.string_identity_resolve(X.doc_to_binder_mentions(d), key="lemma_head")) for d in gentle]
        gbase = [X.per_doc_agg(X.situation_predict_resolve(X.doc_to_binder_mentions(d), gaz, bridge="off")[1]) for d in gentle]
        glive = X._liveschema_perdoc(gentle)
        gsid_v, gn = a(gsid); gbase_v, _ = a(gbase); glive_v, _ = a(glive)
        chk("W12 OOD (GENTLE, n=%d): binder trails floor AND the fix beats both (direction+magnitude generalize)" % gn,
            gbase_v < gsid_v and glive_v > gsid_v and glive_v > gbase_v,
            "floor=%.4f binder=%.4f liveschema=%.4f (fix-floor=%+.4f, matches GUM +0.0252)" % (
                gsid_v, gbase_v, glive_v, glive_v - gsid_v))

    print("=" * 96)
    print("WITNESS: typed-coref re-port onto the LIVE binder path (GUM modern TEST, %d docs, %d labels, n_common=%d)"
          % (len(test), n_lbl, n))
    print("  string_identity(floor)=%.4f  binder_base=%.4f  binder+genbridge=%.4f  urg_binding=%.4f  ORGAN=%.4f"
          % (sid_v, base_v, bra_v, urgb_v, organ_v))
    print("-" * 96)
    npass = 0
    for name, ok, detail in checks:
        print("[%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
        npass += int(ok)
    print("=" * 96)
    print("%d/%d CHECKS PASS" % (npass, len(checks)))
    print("=" * 96)
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
