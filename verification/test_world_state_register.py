"""Scaffold-free witness for situation_model_has_no_mutable_world_state_register.

Recomputes every headline FROM SOURCE (runs the experiment functions, does NOT read cached metrics.json):
  1. the mutable-register CORE (possession transfer, change-point flip, re-toggle, precondition violation);
  2. the MECHANISM proof -- register beats the strongest stateless floor CI-separated, both info-free twins
     lose, change-point control fires (exp_world_state_query_v1);
  3. the PRECONDITION-READ control -- register detects precondition violations CI-separated over an ever-had
     baseline that lacks a mutable state (exp_world_state_precondition_v1);
  4. the EXTRACTION residual -- mechanism ceiling ~1.0, explicit lexicalized transfers recover near-ceiling,
     IMPLICIT stative transfers are the located wall (exp_world_state_extraction_v1).

Run: .venv/Scripts/python.exe verification/test_world_state_register.py
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.world_state_register as W
import experiments.exp_world_state_query_v1 as Q
import experiments.exp_world_state_precondition_v1 as P
import experiments.exp_world_state_extraction_v1 as X
import experiments.possession_operators as PO
import experiments.exp_world_state_learn_operators_v1 as LRN
import experiments.exp_world_state_realtext_mcscript_v1 as RT

CHECKS = []


def chk(name, cond):
    CHECKS.append((name, bool(cond)))
    print("  [%s] %s" % ("PASS" if cond else "FAIL", name), flush=True)


def main():
    print("== 1. CORE (spaCy-free mutable register) ==", flush=True)
    chk("core self-test (transfer chain / change-point flip / re-toggle / precondition violation)",
        W.self_test() == 0)

    print("== 2. MECHANISM: register vs strongest stateless floor (exp_world_state_query_v1) ==", flush=True)
    q = Q.run(mode="full", n_boot=600, seed=20260901)
    sf = q["strongest_floor"]
    chk("register acc == 1.000", q["acc"]["register"]["acc"] == 1.0)
    chk("register CI-lower > strongest floor (%s) CI-upper" % sf,
        q["acc"]["register"]["ci"][0] > q["acc"][sf]["ci"][1])
    chk("register - strongest_floor CI-separated above 0", q["register_minus_strongest_floor"]["sep_above"])
    chk("info-free twin_order LOSES CI-sep", q["register_minus_twin_order"]["sep_above"])
    chk("info-free twin_bind LOSES CI-sep", q["register_minus_twin_bind"]["sep_above"])
    chk("empty register LOSES CI-sep", q["register_minus_empty"]["sep_above"])
    chk("change-point: 100%% of has-items FLIP, 0%% constant",
        q["change_point"]["frac_has_items_that_flip"] == 1.0 and q["change_point"]["frac_constant"] == 0.0)
    chk("strongest floor fails on >=2 distinct qtypes (broad win, not one-structure)",
        sum(1 for v in q["qtype"].values() if v[sf] < 0.5) >= 2)
    chk("mechanism VERDICT PASS", q["PASS"])

    print("== 3. PRECONDITION-READ control (exp_world_state_precondition_v1) ==", flush=True)
    p = P.run(mode="full", n_boot=600, seed=20260901)
    st = p["strongest_trivial"]
    chk("balanced base rate (no constant baseline can exceed ~0.5)", abs(p["base_rate_unmet"] - 0.5) <= 0.05)
    chk("register detects violations acc == 1.000", p["acc"]["register"]["acc"] == 1.0)
    chk("register CI-lower > strongest trivial (%s) CI-upper" % st,
        p["acc"]["register"]["ci"][0] > p["acc"][st]["ci"][1])
    chk("register - strongest_trivial CI-separated", p["register_minus_strongest_trivial"]["sep_above"])
    chk("ever-had baseline FAILS the unmet-after-transfer cases (< 0.5 on give/lose)",
        p["qtype"]["poss_unmet_after_give"]["ever_had"] < 0.5 and p["qtype"]["poss_unmet_after_lose"]["ever_had"] < 0.5)
    chk("precondition VERDICT PASS", p["PASS"])

    print("== 4. EXTRACTION residual (exp_world_state_extraction_v1) ==", flush=True)
    chk("extraction adapter self-test (parses a transfer chain to holder=Cara)", X.self_test() == 0)
    x = X.run(mode="full", n_boot=400, seed=20260901)
    r = x["RESIDUAL"]
    chk("mechanism ceiling on gold effects ~1.0", r["mechanism_ceiling_on_gold_effects"] >= 0.98)
    chk("EXPLICIT lexicalized transfers recover near-ceiling (>= 0.9)", r["extraction_explicit"] >= 0.9)
    chk("recipient (dative/to-PP) recovered on explicit prose (>= 0.9)",
        x["component_recall_explicit"]["recipient"] >= 0.9)
    chk("IMPLICIT stative transfers are the located wall (< 0.1)", r["extraction_implicit"] < 0.1)
    chk("residual is EXTRACTION (implicit), not mechanism",
        r["implicit_residual_explicit_minus_implicit"] >= 0.8)

    print("== 5. OPERATORS FROM WHAT WE HAVE (FrameNet; possession_operators) ==", flush=True)
    chk("FrameNet operator lexicon self-test (give->GIVE, buy/borrow->GET, recipient role recovered)",
        PO.self_test() == 0)
    lex = PO.build_lexicon(use_cache=True)
    chk("lexicon is resource-scale (>= 80 transfer verbs, more than a hand list)", len(lex) >= 80)
    chk("'give' carries a RECIPIENT role from FrameNet (the slot the stock front-end lacked)",
        bool(lex.get("give", {}).get("roles", {}).get("recipient")))

    print("== 6. LEARN-AND-ADAPT: operators induced from exposure (exp_world_state_learn_operators_v1) ==", flush=True)
    lr = LRN.run(mode="full", n_boot=400, seed=20260901)
    chk("learned operators recover FrameNet gold >= 0.9", lr["recovery_learned_vs_framenet_gold"]["acc"] >= 0.9)
    chk("recovery CI-separated above the shuffle twin", lr["recovery_minus_twin"]["sep_above"])
    chk("abstains on a non-transfer verb (no false learning)", lr["abstain_on_nontransfer_verb"])
    chk("register driven by LEARNED operators is usable downstream (>= 0.8)",
        lr["downstream_holder_acc_learned"]["ci"][0] >= 0.8)
    chk("learning VERDICT PASS", lr["PASS"])

    print("== 7. OPEN TEXT via the substrate's OWN parser (exp_world_state_realtext_mcscript_v1) ==", flush=True)
    chk("recipient IS recoverable from the substrate's own parse (self-test)", RT.self_test() == 0)
    rt = RT.run(mode="smoke")
    chk("transfer operators fire densely on REAL narrative (>= 50 instances in the sample)",
        rt["n_transfer_instances"] >= 50)
    chk("recipient recovery on real GIVEs is > 0 (was 0 with the stock extract_args)",
        (rt["role_recovery"]["recipient_on_GIVE"] or 0) > 0.0)
    chk("open-text residual is located to COREF (majority of real agents are pronouns)",
        (rt["coref_gap_agent_is_pronoun_frac"] or 0) >= 0.5)

    print("== 8. DOWNSTREAM: does it break the aligner's before/after wall? (exp_world_state_serves_order_mcscript_v1) ==", flush=True)
    try:
        import experiments.exp_world_state_serves_order_mcscript_v1 as SO
        so = SO.run(mode="smoke", n_boot=200)
        chk("FrameNet adds transfer verbs the aligner's hand sets lacked (>= 20 new)",
            so["possession_verb_coverage"]["n_new_verbs"] >= 20)
        chk("the ~0.59 wall HOLDS -- possession does NOT break before/after ordering (order is conventional)",
            not so["WALL_broken"])
    except Exception as e:
        chk("order-wall serve test ran (harness importable)", False)
        print("     (order test error: %s)" % e, flush=True)

    n_pass = sum(1 for _, ok in CHECKS if ok)
    n = len(CHECKS)
    print("\n%d/%d checks PASS" % (n_pass, n), flush=True)
    return 0 if n_pass == n else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
