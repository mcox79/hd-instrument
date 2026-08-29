"""Scaffold-free witness for pronoun_to_event_binding_caps_who_did_what.

Asserts the load-bearing claims of the PARTIAL result without the full run:
  1. MECHANISM + POSITIVE CONTROL: the focus-driven graded binder binds a Cb-decisive pronoun the ACT-R
     incumbent mis-binds (the metric CAN move).
  2. THE LIFT: the full brain-faithful binder (graded cues + gender agreement) lifts who-did-what
     pronoun-query accuracy over the ACT-R incumbent, and the info-free RANDOM-binding twin LOSES; the
     perfect-binding ceiling is far above both (the headroom is real).
  3. THE STRUCTURAL-CUE NULL (the drilled wall): on CLEAN teacher-forced binding, ACT-R base-level
     activation is already optimal -- no geometry-heavy hand-config (subject/cb/centering) beats pure
     ACT-R. So the tracked Cb/clause_role cue adds ~0 on clean binding; the modest online lift is a
     generic richer-binder effect, not a clean Cb attribution.
  4. THE DECOMPOSITION: the live in-harness binder binds to the gold anchor only ~0.23 (vs 0.78 clean),
     and even PERFECT binding decodes only ~0.61 (the definitional decode ceiling) -- the +0.44 headroom
     is binding + a large fixed ceiling, not cue-weighting.

Run: .venv/Scripts/python.exe verification/test_coref_graded_binder_serves_whodidwhat.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.exp_coref_graded_binder_serves_whodidwhat_v1 import (  # noqa: E402
    self_test, positive_control, cell, reinstrument)
from experiments.exp_coref_binder_wall_diagnostic_v1 import run as wall_run, in_harness_binding  # noqa: E402


def main():
    checks = []

    # 1. mechanism + positive control
    self_test()
    checks.append(("mechanism self-test (Cb/focus cues fire; graded net picks the sustained topic)", True))
    pc = positive_control()
    checks.append(("positive control MOVES: graded binds the Cb-decisive pronoun, ACT-R mis-binds",
                   pc["graded_binds_Cb_correct"] and not pc["actr_binds_Cb_correct"]))

    # 2. the lift + info-free random twin loses (small subset; directional)
    m = cell(docs=30, n_boot=400)
    ap = m["accuracy_pronoun_TEST"]
    head = ap["HEAD"]["acc"]; grad_ag = ap["HEAD_GRADED_AGREE"]["acc"]
    ceil = ap["HEAD_OPB"]["acc"]; rand = ap["HEAD_RANDBIND"]["acc"]
    checks.append((f"full binder lifts who-did-what over ACT-R incumbent ({grad_ag:.3f} > {head:.3f})",
                   grad_ag > head))
    checks.append((f"info-free RANDOM-binding twin LOSES ({rand:.3f} < {grad_ag:.3f})", rand < grad_ag - 0.02))
    checks.append((f"perfect-binding ceiling is far above the floor ({ceil:.3f} >> {head:.3f}) -> headroom real",
                   ceil > head + 0.30))

    # 3. the structural-cue null on CLEAN teacher-forced binding: ACT-R is already optimal
    w = wall_run(docs=30, n_boot=200)
    hc = w["hand_config_binding_acc_TEST_all"]
    geom_best = max(hc["subject_heavy"], hc["cb_heavy"], hc["subject_cb_first"], hc["centering_only"])
    checks.append((f"pure ACT-R ({hc['pure_actr']:.3f}) >= every geometry-heavy hand-config "
                   f"({geom_best:.3f}) -> tracked Cb/clause_role adds ~0 on clean binding",
                   hc["pure_actr"] >= geom_best - 1e-6))
    ga = w["ALL_pronouns_TEST"]["contrasts"]["graded_minus_actr"]
    checks.append((f"graded ties ACT-R on clean binding ({ga['delta']:+.3f}, not ABOVE)",
                   ga["band"] != "ABOVE"))
    dom = w["graded_error_anatomy_TEST_all"]["frac_gold_structurally_DOMINATED_needs_semantics"]
    checks.append((f"a real semantic core: {dom:.2f} of binding errors structurally DOMINATED (needs semantics)",
                   dom > 0.1))

    # 4. the decomposition: live binder binds ~0.23; perfect binding decodes ~0.61 (definitional ceiling)
    ih = in_harness_binding(docs=30)
    head_bind = ih["HEAD"]["bound_to_gold_anchor_frac"]
    opb_bind = ih["HEAD_OPB"]["bound_to_gold_anchor_frac"]
    opb_decode = ih["HEAD_OPB"]["who_did_what_decode_frac"]
    checks.append((f"live in-harness binder binds to the gold anchor only {head_bind:.2f} (vs ~0.78 clean)",
                   head_bind < 0.40))
    checks.append((f"perfect binding ({opb_bind:.2f}) still decodes only {opb_decode:.2f} -> definitional "
                   f"decode ceiling caps the +0.44 headroom", opb_bind > 0.95 and 0.5 < opb_decode < 0.7))

    # 5. THE PROVEN FIX: re-instrument the readout as a situation-model event-set -> the ceiling was a
    #    metric artifact (jumps toward 1.0), and the binder still lifts CI-sep with the twin losing.
    ri = reinstrument(docs=30, n_boot=300)
    ceil_old = ri["ceiling_OLD_HEAD_OPB"]; ceil_new = ri["ceiling_NEW_HEAD_OPB"]
    checks.append((f"re-instrumentation lifts the ceiling {ceil_old:.2f} -> {ceil_new:.2f} (the 0.61 ceiling "
                   f"was a METRIC ARTIFACT of the per-sentence collapse)",
                   ceil_new > 0.90 and ceil_new > ceil_old + 0.25))
    bl = ri["binder_lift_NEW"]
    # subset (docs=30, ~15 test docs): assert DIRECTION of the lift + the random-twin control losing
    # CI-sep; the CI-separation of the lift itself is established in the FULL 100-doc run (+0.085 ABOVE).
    checks.append((f"under the faithful readout the binder lifts directionally ({bl['delta']:+.3f}) "
                   f"and the random twin loses CI-sep", bl["delta"] > 0.0
                   and ri["binder_over_randtwin_NEW"]["band"] == "ABOVE"))

    # 6. THE RESIDUAL MECHANISM PROVEN: the discourse-specific-memory signal (situation model) recovers
    #    the anti-typical residual where GENERIC typicality is dead -- so the wall is a missing situation
    #    model, not a capability ceiling (the "if the brain can do it, so can we" answer, measured).
    from experiments.exp_coref_residual_discourse_specific_v1 import run as ds_run
    ds = ds_run()
    dso = ds["DISCOURSE_SPECIFIC_oracle_verb_or_obj"]
    generic = ds["GENERIC_typicality_prior_on_residual"]["combined"]
    twin = ds["info_free_twin_shuffled_affinity"]["acc_on_covered"]
    checks.append((f"discourse-specific memory recovers residual where typicality is dead "
                   f"(covered acc {dso['acc_on_covered']:.3f} > twin {twin:.3f} and > generic {generic:.3f}; "
                   f"coverage {dso['coverage_frac']:.2f})",
                   dso["acc_on_covered"] > twin + 0.05 and dso["acc_on_covered"] > generic
                   and dso["coverage_frac"] > 0.3))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
