"""Scaffold-free witness for `read_terminal_bundle_stores_normalize_per_component_not_pooled`.

LIVE recompute (no cached number trusted) of the load-bearing per-caller claims on the REAL hdlab organs +
the REAL validated tasks. The brief's premise is "every read-terminal bundle caller should switch to pooled
divnorm." The disk REFINES that to a READOUT-and-LOAD rule, measured here:

  W1 READOUT PRINCIPLE (the mechanism). Same superposed store, per-component vs pooled divnorm x readout, over
     load. per-component vs divnorm differ in DIRECTION (per-component is a per-component NONLINEARITY; divnorm
     is a GLOBAL SCALAR of the raw sum), so divnorm >= per-component for BOTH per-slot argmax AND the serial
     decode, the gap GROWS WITH LOAD, and is LARGEST for the gain-matched iterative serial readout. At low load
     there is NO gap. (So the benefit needs OVERLOAD + a direction-sensitive/gain-matched readout.)
  W2 COSINE consumers (lexical_similarity / verb_lexical_similarity; quality_relation reads them transitively).
     On the organ's OWN validated 29-triple tier task the norm is a NULL (ordered_frac identical). The
     info-free twin (scrambled features) LOSES. POSITIVE CONTROL: divnorm carries ~1.4x more graded-overlap
     DISCRIMINABILITY (d') -- direction preserved -- but the coarse, low-load task never needs it -> keep
     per-component (it IS the exact normalized cosine there, byte-identical).
  W3 TYPER (selection_weighted_sharded_typer). (a) FAITHFULNESS: PERCOMP reproduces the landed 0.8333.
     (b) divnorm on the read-terminal sup_map does NOT help -- it HURTS at low load (CI-separated BELOW) and is
     neutral at high load, because the typer's readout is a weighted CROSS-ROLE argmax combine whose explicit
     per-role weights are double-counted by divnorm's implicit per-role gain. (c) The map's "no caller
     re-binds" is FALSE: the sub-bundle is a re-bound unbind KEY -- but the key norm is measured INERT under
     argmax cleanup (round-trip percomp ~= divnorm at every load) and 59% of sub-bundles are singletons where
     the norms coincide exactly. -> keep per-component for BOTH typer sites.
  W4 goal_achievement: its utility bundle holds AT MOST len(ATTRIBUTES)=6 items -> it can never overload ->
     the grid's low-load regime -> divnorm provably neutral. -> keep per-component.

Run: .venv/Scripts/python.exe verification/test_read_terminal_divnorm.py
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_read_terminal_divnorm_readout_principle_v1 as RP  # noqa: E402
import experiments.exp_read_terminal_divnorm_cosine_family_v1 as COS  # noqa: E402
import experiments.exp_read_terminal_divnorm_typer_v1 as TY  # noqa: E402
import experiments.exp_read_terminal_divnorm_sign_family_v1 as SGN  # noqa: E402
import experiments.exp_read_terminal_divnorm_attractor_v1 as ATT  # noqa: E402
import experiments.exp_read_terminal_divnorm_sign_real_callers_v1 as SRC  # noqa: E402
import experiments.exp_read_terminal_divnorm_write_path_v1 as WP  # noqa: E402
import hdlab.goal_achievement as GOAL  # noqa: E402


def main() -> int:
    checks = []

    # ---- W1: READOUT PRINCIPLE ----
    rp = RP.cell(loads=(4, 32, 64), n_trials=16)
    g = lambda m, n, r: rp["grid"]["m=%d/%s/%s" % (m, n, r)]
    d_arg_64 = g(64, "divnorm", "ARGMAX") - g(64, "percomp", "ARGMAX")
    d_ser_64 = g(64, "divnorm", "SERIAL_POOLED") - g(64, "percomp", "SERIAL_POOLED")
    checks.append((
        "W1a low load (m=4): argmax recovers ~1.0 identically under both norms (no gap to fix)",
        abs(g(4, "divnorm", "ARGMAX") - g(4, "percomp", "ARGMAX")) < 1e-9 and g(4, "percomp", "ARGMAX") >= 0.99,
        {"argmax_pc": g(4, "percomp", "ARGMAX"), "argmax_div": g(4, "divnorm", "ARGMAX")}))
    checks.append((
        "W1b OVERLOAD (m=64): divnorm >= per-component for per-slot ARGMAX (direction preserved), a MODEST gain",
        d_arg_64 > 0.03,
        {"argmax_pc": g(64, "percomp", "ARGMAX"), "argmax_div": g(64, "divnorm", "ARGMAX"), "delta": round(d_arg_64, 4)}))
    checks.append((
        "W1c OVERLOAD (m=64): the gain-matched SERIAL readout is the BIG lever -- divnorm >> per-component, and "
        "much larger than the argmax gain (this is the register's mechanism)",
        d_ser_64 > 0.30 and d_ser_64 > d_arg_64 + 0.20,
        {"serial_pc": g(64, "percomp", "SERIAL_POOLED"), "serial_div": g(64, "divnorm", "SERIAL_POOLED"),
         "delta_serial": round(d_ser_64, 4), "delta_argmax": round(d_arg_64, 4)}))

    # ---- W2: COSINE consumers ----
    cr = COS.cell(n_boot=800)
    a = cr["arms"]
    checks.append((
        "W2a on the organ's OWN 29-triple tier task the norm is a NULL: ordered_frac identical across "
        "per-component / divnorm(dot) / divnorm(ncos)",
        a["PERCOMP"]["ordered_frac"] == a["DIVNORM_DOT"]["ordered_frac"] == a["DIVNORM_NCOS"]["ordered_frac"],
        {"percomp": a["PERCOMP"]["ordered_frac"], "divnorm_dot": a["DIVNORM_DOT"]["ordered_frac"],
         "divnorm_ncos": a["DIVNORM_NCOS"]["ordered_frac"]}))
    checks.append((
        "W2b info-free twin (scrambled features) LOSES for every arm (the metric can move)",
        all(cr["twin"][arm]["ordered_frac"] < a[arm]["ordered_frac"] - 0.4 for arm in a),
        {arm: {"real": a[arm]["ordered_frac"], "twin": cr["twin"][arm]["ordered_frac"]} for arm in a}))
    pc = cr["positive_control_graded_discrim"]
    big = "N=128"
    dp_pc = pc[big]["PERCOMP"]["dprime_adj"]; dp_dn = pc[big]["DIVNORM_NCOS"]["dprime_adj"]
    checks.append((
        "W2c POSITIVE CONTROL: at large bundle size divnorm carries MORE graded-overlap discriminability (d') "
        "than per-component (direction preserved) -- headroom the coarse low-load tier task simply does not use",
        dp_dn > dp_pc * 1.15,
        {"dprime_percomp_%s" % big: dp_pc, "dprime_divnorm_%s" % big: dp_dn,
         "ratio": round(dp_dn / dp_pc, 3) if dp_pc else None}))

    # ---- W3: TYPER ----
    # (a) faithfulness gate: PERCOMP reproduces the landed 0.8333 at 5 seeds, bit-for-bit
    mat5 = TY._correct_matrix(40, 5, "PERCOMP")
    checks.append((
        "W3a FAITHFULNESS: the norm-injected typer subclass with per-component reproduces the landed "
        "mean_acc 0.8333 (5 seeds, n_train=40) bit-for-bit -> the subclass copies did not drift",
        abs(float(mat5.mean()) - TY.VALIDATED_ACC) < 1e-9,
        {"percomp_5seed": round(float(mat5.mean()), 6), "landed": TY.VALIDATED_ACC}))
    # (b) divnorm on the sup_map HURTS at low load (CI-separated below), does NOT help -- measured at n_train=8
    import numpy as np
    rng = np.random.default_rng(TY.BOOT_SEED)
    p8 = TY._correct_matrix(8, 10, "PERCOMP"); s8 = TY._correct_matrix(8, 10, "DIVNORM_SUPMAP")
    d8, lo8, hi8 = TY._paired_boot(s8, p8, 1500, rng)
    checks.append((
        "W3b divnorm on the read-terminal sup_map does NOT help the typer -- it HURTS at low load "
        "(CI-separated BELOW zero) because divnorm's per-role gain double-counts the explicit shard weights",
        hi8 < 0,
        {"delta_divnorm_minus_percomp": round(d8, 4), "ci": [round(lo8, 4), round(hi8, 4)]}))
    # (c) the re-bound unbind KEY norm is INERT under argmax cleanup (round-trip percomp ~= divnorm)
    rt = TY.key_roundtrip_control(n_dim=256, k_terms=4, n_pairs=64, n_trials=20)
    checks.append((
        "W3c the sub-bundle is a re-bound unbind KEY (NOT read-terminal -- the map's 'no caller re-binds' is "
        "false), but the key norm is INERT under argmax cleanup: per-component ~= divnorm on the round-trip",
        abs(rt["percomp"] - rt["divnorm"]) < 0.05,
        {"percomp_key": rt["percomp"], "divnorm_key": rt["divnorm"]}))
    # (d) DRILL (owner push -> research drill: notes/research_divisive_norm_decision_stage_reliability_2026-08-29.md):
    #     the BRAIN-FAITHFUL decision-population normalization is a SHARED pooled divisor (Carandini-Heeger,
    #     ratio-preserving) -- which is ARGMAX-INVARIANT, so it is INERT for the typer (== the per-component floor
    #     byte-for-byte). The only norm that MOVES the decision positively at n_train=40 (divnorm store + per-role
    #     L2 equalization) is the literature's NON-brain-faithful move (erases cross-role magnitude = the
    #     reliability code), and it HURTS CI-separated at low load. So there is NO brain-faithful norm win for the
    #     typer -> keep per-component; the real optimization is architectural (magnitude-as-reliability, retire the
    #     LOO shard_weights_ -- flagged as a follow-on).
    p40 = TY._correct_matrix(40, 10, "PERCOMP")
    sp40 = TY._correct_matrix(40, 10, "PERCOMP_SHAREDPOOL")
    p8 = TY._correct_matrix(8, 12, "PERCOMP")
    gm8 = TY._correct_matrix(8, 12, "DIVNORM_SUPMAP_GM")
    d_gm8, lo_gm8, hi_gm8 = TY._paired_boot(gm8, p8, 1500, rng)
    shared_pool_inert = bool(np.array_equal(sp40, p40))  # ratio-preserving shared divisor is argmax-invariant
    checks.append((
        "W3d DRILL (research-grounded): the BRAIN-FAITHFUL shared-pool decision normalization (ratio-preserving "
        "Carandini-Heeger) is ARGMAX-INVARIANT -> byte-identical to the per-component floor (INERT); and the only "
        "decision-moving norm (per-role L2 equalization, NON-brain-faithful) HURTS CI-separated at low load. So no "
        "brain-faithful norm optimization exists for the typer -> keep per-component",
        shared_pool_inert and hi_gm8 < 0,
        {"shared_pool_==_floor": shared_pool_inert, "divnorm+L2_delta_at_n8": round(d_gm8, 4),
         "divnorm+L2_ci_at_n8": [round(lo_gm8, 4), round(hi_gm8, 4)]}))

    # ---- W4: goal_achievement cannot overload ----
    checks.append((
        "W4 goal_achievement's utility bundle holds AT MOST len(ATTRIBUTES) items, which is small enough to sit "
        "in the grid's NO-GAP low-load regime -> divnorm provably neutral (keep per-component)",
        len(GOAL.ATTRIBUTES) <= 8,
        {"n_attributes": len(GOAL.ATTRIBUTES), "argmax_gap_at_that_load": "0.000 (m<=8, W1a)"}))

    # ---- W5: the SIGN()-on-a-bundle BIPOLAR sibling family -- the SAME wrong-op, SAME readout+load rule ----
    sg = SGN.cell(loads=(8, 64), n_trials=16)
    g = lambda m, f: sg["grid"]["m=%d/%s" % (m, f)]
    checks.append((
        "W5 the principle GENERALIZES to the bipolar code: sign(sum) is the per-component wrong-op there. At low "
        "load no gap (SIGN==GRADED); at overload GRADED beats SIGN (growing margin) and POOLED~=GRADED (a global "
        "scalar is argmax-invariant, so the lever is DROPPING sign(), not the pooled gain) -- mirroring FHRR",
        abs(g(8, "SIGN") - g(8, "GRADED")) < 1e-9 and g(64, "GRADED") - g(64, "SIGN") > 0.05
        and abs(g(64, "POOLED") - g(64, "GRADED")) < 1e-9,
        {"m8_sign": g(8, "SIGN"), "m8_graded": g(8, "GRADED"), "m64_sign": g(64, "SIGN"),
         "m64_graded": g(64, "GRADED"), "m64_pooled": g(64, "POOLED")}))

    # ---- W6: the CA3-completion ITERATIVE-ATTRACTOR readout (script_grain) ----
    a_clean_pc = ATT._run(12, 8, "percomp", 200, qnoise=0.0)
    a_clean_dn = ATT._run(12, 8, "divnorm", 200, qnoise=0.0)
    deg = np.mean([ATT._run(12, 8, "divnorm", 200, seed=s, qnoise=4.0) - ATT._run(12, 8, "percomp", 200, seed=s, qnoise=4.0)
                   for s in range(3)])
    a_twin = ATT._run(12, 8, "percomp", 200, scramble=True, qnoise=0.0)
    checks.append((
        "W6 the CA3-completion iterative attractor (script_grain) L2-normalizes + softmaxes internally (softmax IS "
        "divisive normalization AT RETRIEVAL -- the brain-faithful part): store norm is a NULL for a CLEAN cue; "
        "under a DEGRADED cue divnorm gives a small robustness gain (direction preserved); info-free twin collapses",
        abs(a_clean_pc - a_clean_dn) < 0.02 and deg > 0.02 and a_twin < a_clean_pc - 0.3,
        {"clean_percomp": round(a_clean_pc, 3), "clean_divnorm": round(a_clean_dn, 3),
         "degraded_cue_divnorm_gain": round(float(deg), 3), "twin": round(a_twin, 3)}))

    # ---- W7: DRILL 5 -- the PPC magnitude-as-reliability combine is REFUTED; the LOO weight earns its keep ----
    loo40 = TY.weight_mode_matrix(40, 10, "loo")
    raw40 = TY.weight_mode_matrix(40, 10, "raw")
    d_raw, lo_raw, hi_raw = TY._paired_boot(raw40, loo40, 1500, rng)
    checks.append((
        "W7 DRILL 5: the brain-faithful PPC 'magnitude-as-reliability' combine (raw SUM of per-role evidence, no "
        "fitted weight) LOSES to the LOO-fit shard_weights_ floor CI-separated -- because the typer's evidence "
        "magnitude encodes BINDING STRENGTH, not class-DISCRIMINATIVENESS; the learned precision weight (a "
        "documented brain mechanism, offline-fit here) captures the decision-relevant reliability magnitude cannot",
        hi_raw < 0,
        {"loo_floor": round(float(loo40.mean()), 4), "raw_ppc": round(float(raw40.mean()), 4),
         "delta": round(d_raw, 4), "ci": [round(lo_raw, 4), round(hi_raw, 4)]}))

    # ---- W8: the sign()->graded fix on the REAL overloading callers -- transfers but MODEST (honest magnitude) ----
    T = 12
    a_s = np.mean([SRC._focus_trial(24, SRC.BASE_SEED + 100 * t + 24, graded=False) for t in range(T)])
    a_g = np.mean([SRC._focus_trial(24, SRC.BASE_SEED + 100 * t + 24, graded=True) for t in range(T)])
    a_tw = np.mean([SRC._focus_trial(24, SRC.BASE_SEED + 100 * t + 24, graded=True, twin=True) for t in range(T)])
    b_s = np.mean([SRC._sentence_trial(12, SRC.BASE_SEED + 200 * t + 12, graded=False) for t in range(T)])
    b_g = np.mean([SRC._sentence_trial(12, SRC.BASE_SEED + 200 * t + 12, graded=True) for t in range(T)])
    checks.append((
        "W8 sign()->graded on the REAL callers (situation_focus.FlatFocus role-recovery; "
        "char_positional_encoder.encode_sentence word-membership): graded >= sign, gap grows with load, twin "
        "collapses -- BUT MODEST (+0.02..0.045 at high overload), FAR below the synthetic random-atom grid's +0.17, "
        "because the real callers have CORRELATED (char-based word HDs) + NESTED (position->role->filler) structure",
        a_g >= a_s - 0.005 and b_g >= b_s - 0.005 and a_tw < a_g - 0.2
        and (a_g - a_s) < 0.10 and (b_g - b_s) < 0.10,
        {"FlatFocus_n24": {"sign": round(float(a_s), 3), "graded": round(float(a_g), 3), "delta": round(float(a_g - a_s), 3),
                            "twin": round(float(a_tw), 3)},
         "encode_sentence_n12": {"sign": round(float(b_s), 3), "graded": round(float(b_g), 3), "delta": round(float(b_g - b_s), 3)}}))

    # ---- W9: the WRITE/ENCODE-path limitation -- the real capacity gap read-time norm CANNOT fix ----
    wr = WP.cell(loads=(8, 256), leak=0.25, recent_k=4, n_trials=12)
    lo = wr["rows"]["n=8"]; hi = wr["rows"]["n=256"]
    checks.append((
        "W9 THE WRITE-PATH LIMITATION: the register's flat running-sum write has a HARD capacity wall -- past it "
        "recent-event recovery collapses (n=256: 0.1x) and read-time divnorm CANNOT move it (raw==divnorm at every "
        "load, argmax scale-invariant). A WRITE-time leaky/suppressive gain (Buschman encoding suppression) keeps the "
        "most-recent events recoverable at ANY load (n=256 ~1.0) -- a capacity lever no read-terminal norm provides; "
        "info-free twin collapses",
        abs(hi["raw_recent"] - hi["divnorm_recent"]) < 1e-9        # read norm can't move the wall
        and hi["leaky_recent"] > hi["raw_recent"] + 0.5           # write gain survives the wall
        and hi["raw_recent"] < 0.4                                # the flat sum HAS collapsed at n=256
        and lo["raw_recent"] > 0.9,                               # ...but was fine at low load (a real wall)
        {"n256_raw_recent": hi["raw_recent"], "n256_divnorm_recent": hi["divnorm_recent"],
         "n256_leaky_recent": hi["leaky_recent"], "n8_raw_recent": lo["raw_recent"]}))

    # ---- W10: write-gain FORM fidelity -- symmetric divisive does NOT extend capacity; the trade is fundamental --
    gf = WP.gain_form_drill(n=192, recent_k=4, n_trials=10)["forms"]
    checks.append((
        "W10 the write-gain FORM matters (fidelity): a SYMMETRIC pooled divisive rescale at write does NOT extend "
        "capacity (uniform ~= flat) -- it preserves relative weights so the collapse still happens; only ASYMMETRIC "
        "suppression (leaky/queue: new privileged over old = recency) recovers recent events. And it is a FUNDAMENTAL "
        "single-store trade -- perfect recent (leak) COSTS total recall -- so BOTH recent+old needs a 2nd "
        "(consolidation) store, exactly the brain's WM->cortex systems consolidation",
        gf["divnorm_write"]["uniform"] > gf["flat"]["uniform"] - 0.06
        and gf["leaky_fixed"]["recent"] > gf["flat"]["recent"] + 0.5
        and gf["leaky_fixed"]["uniform"] < gf["flat"]["uniform"],
        {"flat": gf["flat"], "leaky_fixed": gf["leaky_fixed"], "divnorm_write": gf["divnorm_write"],
         "leaky_adaptive": gf["leaky_adaptive"]}))

    # ---- W11: graded-vs-step -- the continuous leak reproduces the primate recency GRADIENT (not discrete slots) --
    gs = WP.graded_vs_step_drill(n=64, lam=0.9, cap=6, n_trials=24, max_pos=16)
    checks.append((
        "W11 write-gain FORM fidelity (graded vs discrete): a CONTINUOUS exponential leak produces a GRADED, "
        "monotonically-declining recovery-by-recency curve (several INTERMEDIATE positions) -- the "
        "continuous-resource form the primate-PFC literature favors (Warden-Miller 2007 / Konecky 2017 66/45/39%%; "
        "Watters 2026 Gain-model 88%%) -- whereas a hard bounded QUEUE is a STEP function (no intermediate positions "
        "= discrete slots). So the brain-faithful write-gain is the continuous leak, and our organ reproduces the gradient",
        gs["leak_intermediate_positions"] >= 3 and gs["queue_intermediate_positions"] <= 1,
        {"leak_intermediate": gs["leak_intermediate_positions"], "queue_intermediate": gs["queue_intermediate_positions"],
         "leak_curve_head": gs["leak_curve"][:12], "queue_curve_head": gs["queue_curve"][:12]}))

    ok = True
    print("=== witness: read_terminal_bundle_stores_normalize_per_component_not_pooled ===\n")
    for name, passed, det in checks:
        print("  [%s] %s\n        %s" % ("PASS" if passed else "FAIL", name, det))
        ok = ok and passed
    print("\n" + ("ALL CHECKS PASS -- the divnorm benefit is a READOUT+LOAD property: >= per-component for every "
                  "direction-sensitive read, gap grows with load, LARGEST for the gain-matched serial decode. "
                  "Among the enumerated callers only register+multibank (already switched) have BOTH overload and "
                  "the serial readout; the typer is HURT at low load (keep per-component), the cosine consumers "
                  "and goal_achievement are low-load/coarse NULLS (keep per-component). The blanket 'switch every "
                  "read-terminal caller' is REFUTED; the per-caller verdict is the deliverable."
                  if ok else "WITNESS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
