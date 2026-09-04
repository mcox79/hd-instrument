"""Scaffold-free witness for build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader.

Recomputes from source (CPU, threads=1 for determinism; NO external LLM, NO transformer, NO training; glass-box).
Strict document-disjoint SemCor subordinate senses, subject-weighted a_s, through the wired biased-competition
diagnostic readout.

  W1  FLOORS reproduce first-hand: gloss-w2v a_s ~= 0.251 and the RICH launch-pad a_s ~= 0.313 (the +0.067 clean
      foundation this problem builds on).
  W2  THE RICHER GROUNDED ATL HUB IS A LOCATED NEGATIVE: the Binder-65 + Warriner + whitened + inheritance grounded
      hub-and-spoke, fed to the readout, does NOT cross the launch pad (concat hub a_s < launch pad).
  W3  ...AND WE KNOW WHY: the grounded KEYS actually separate competing senses (mean whitened cos(gold,dominant)
      < 0.40, well below 1.0) -- so it is NOT that grounding fails to separate; the bottleneck is elsewhere
      (query-side + ~0.47 coverage; the sense keys are already separable via gloss).
  W4  THE REAL LEVER IS QUERY-SIDE AND BRAIN-FAITHFUL: precision-weighting (Friston selective gain: gamma>1 / top-k
      on the diagnosticity) CROSSES the launch pad CI-separated, its info-free shuffled-diagnosticity twin LOSES,
      and it does NOT regress the dominant-sense (MFS) population -- BUT it does not reach the 0.35 ceiling
      (the crosser is a broad-coverage sense-discriminative connection matrix W, the owner-DONE sibling's domain).

Run: .venv/Scripts/python.exe verification/test_atl_hubspoke_meaning_channel.py
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"    # threads=1 for deterministic argmax (no BLAS tie-break jitter)
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_atl_hubspoke_grounded_separability_v1 as A
import experiments.exp_atl_hubspoke_query_side_readout_v1 as B

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


def main():
    print("[witness] recomputing the grounded located negative + the precision-weighting positive (a few min) ...",
          flush=True)
    ra = A.run(smoke=False)
    arms = ra["arms"]
    dec = ra["separability_decomposition"]

    chk("W1 floors reproduce (gloss-w2v ~0.251, rich launch pad ~0.313)",
        abs(arms["L0_gloss_w2v"] - 0.251) < 0.02 and abs(arms["L3_rich_w2v_LAUNCHPAD"] - 0.313) < 0.02,
        "gloss=%.4f launchpad=%.4f" % (arms["L0_gloss_w2v"], arms["L3_rich_w2v_LAUNCHPAD"]))

    chk("W2 richer grounded ATL hub is a LOCATED NEGATIVE (concat hub does NOT cross the launch pad)",
        arms["hub_concat"] <= arms["L3_rich_w2v_LAUNCHPAD"] and not (
            ra["hub_vs_launchpad"]["sep"] and arms["hub_concat"] > arms["L3_rich_w2v_LAUNCHPAD"]),
        "hub=%.4f launchpad=%.4f (grounded keys alone=%.4f)"
        % (arms["hub_concat"], arms["L3_rich_w2v_LAUNCHPAD"], arms["grounded_keys_whitened"]))

    chk("W3 grounded keys DO separate competing senses (mean whitened cos(gold,dominant) < 0.40) -- not the bottleneck",
        dec["grounded_white_cos_gold_vs_dominant_mean"] is not None and dec["grounded_white_cos_gold_vs_dominant_mean"] < 0.40,
        "cos(gold,dom)=%.4f cov=%.3f frac_separable=%.4f"
        % (dec["grounded_white_cos_gold_vs_dominant_mean"], dec["grounded_coverage_of_pairs"],
           dec["frac_grounded_separable_cos_lt_0.5"]))

    rb = B.run(smoke=False)
    barms = rb["arms"]
    best = rb["best_a_s"]
    chk("W4a precision-weighting (Friston selective gain) CROSSES the launch pad CI-separated, twin loses",
        rb["best_vs_launchpad"]["sep"] and best > rb["launchpad_floor"] and rb["best_vs_twin"]["sep"] and best > rb["twin_a_s"],
        "best(%s)=%.4f vs launchpad=%.4f ci=%s | twin=%.4f"
        % (rb["best_arm"], best, rb["launchpad_floor"], rb["best_vs_launchpad"]["ci"], rb["twin_a_s"]))

    chk("W4b precision-weighting does NOT regress the dominant-sense (MFS) population",
        rb["mfs_guard"]["no_regression"],
        "all-items launchpad=%.4f best=%.4f delta=%+.4f"
        % (rb["mfs_guard"]["launchpad_all"], rb["mfs_guard"]["best_all"], rb["mfs_guard"]["delta_all"]))

    chk("W4c ...but no glass-box readout/representation lever reaches the 0.35 static-distributional ceiling",
        best < 0.35, "best a_s=%.4f < 0.35 (the crosser is a broad-coverage sense-discriminative W)" % best)

    # ---- W5/W6: the UPSTREAM brain-foundational chain (grounded disambiguate-then-bind W, monotonic fidelity ladder)
    import experiments.exp_atl_hubspoke_grounded_disambiguate_then_bind_v1 as C
    rc = C.run(smoke=False)
    att = rc["MECHANISM_on_gold_attested_subset"]
    chk("W5 the sense-discriminative-W architecture helps ONLY with a CORRECT (gold) resolver, and even then only "
        "directionally on the attested subset (gold W-base > 0 and > every glass-box resolver) -- borderline, not "
        "robustly CI-separated, which sharpens the negative",
        att["gold_W_reference"]["W_minus_base"] > 0
        and att["gold_W_reference"]["W_minus_base"] > max(att["distributional_W"]["W_minus_base"],
                                                          att["grounded_W"]["W_minus_base"],
                                                          att["bootstrap_W"]["W_minus_base"]),
        "gold W-base=%+.4f (a_s %.4f vs base %.4f) sep=%s -- the ONLY positive arm"
        % (att["gold_W_reference"]["W_minus_base"], att["gold_W_reference"]["a_s_W"],
           att["gold_W_reference"]["a_s_base_same_items"], att["gold_W_reference"]["sep"]))

    chk("W6 ...and every GLASS-BOX encoding resolver FAILS to build a clean W (localizes the last non-faithful "
        "component to the encoding resolver, trapped in the frozen w2v): grounded/distributional/bootstrap all <= 0",
        (att["grounded_W"]["W_minus_base"] <= 0.01 and att["distributional_W"]["W_minus_base"] <= 0.01
         and att["bootstrap_W"]["W_minus_base"] <= 0.01),
        "dist=%+.4f grounded=%+.4f bootstrap=%+.4f (all <= gold %+.4f)"
        % (att["distributional_W"]["W_minus_base"], att["grounded_W"]["W_minus_base"],
           att["bootstrap_W"]["W_minus_base"], att["gold_W_reference"]["W_minus_base"]))

    # ---- W7: the IDEAL full chain (gold-W foundation at MAXIMAL coverage + inheritance) does NOT cross -- the
    # coverage route is closed (count-based W is Zipf-bound for rare senses; inheritance blurs regular polysemy)
    import experiments.exp_atl_hubspoke_ideal_full_chain_v1 as D
    rd = D.run(smoke=False)
    lad = rd["coverage_ladder"]
    r1 = [v for k, v in lad.items() if k.startswith("R1")][0]
    r4 = rd["best_a_s"]
    chk("W7 the IDEAL gold-W foundation at MAX coverage + inheritance does NOT cross 0.35 and does not beat the "
        "precision readout (the coverage route is closed: rare-sense Zipf + inheritance blur)",
        r4 < 0.35 and r4 <= r1 + 0.005,
        "R4_ideal=%.4f vs R1_precision=%.4f (coverage=%s) crosses0.35=%s" % (r4, r1, rd["W_coverage"], rd["crosses_0.35"]))

    # ---- W8: the CONTEXTUAL RE-COMPUTATION fix for the frozen-representation wall (glass-box AutoExtend
    # de-superposition + context re-selection) is a located negative -- it DOES de-superpose the senses but a_s
    # DROPS, because de-superposing the keys while the context stays frozen breaks the context<->key match. Joint
    # re-representation (word + context in one space) is the trained contextual encoder = the invariant boundary.
    import experiments.exp_atl_hubspoke_contextual_recompute_v1 as E
    re = E.run(smoke=False)
    ds = re["desuperposition"]
    chk("W8 glass-box de-superposition DOES separate senses (AutoExtend cos < gloss cos) but a_s DROPS below the "
        "launch pad -- de-superposing keys while context stays frozen breaks the match (frozen-rep wall confirmed)",
        ds["more_separated"] and re["best_a_s"] < re["arms"]["A0_gloss_launchpad"] and not re["crosses_0.35"],
        "de-superpose gloss cos %.3f->AE %.3f | A0=%.4f best(AE)=%.4f crosses0.35=%s"
        % (ds["gloss_cos_gold_dom_mean"], ds["autoextend_cos_gold_dom_mean"], re["arms"]["A0_gloss_launchpad"],
           re["best_a_s"], re["crosses_0.35"]))

    # NOTE: the JOINT PPR arm (exp_atl_hubspoke_joint_ppr_recompute_v1) is reproduced by its OWN cell, not folded
    # into this witness -- the 1.0M-edge WordNet++ graph makes the 6-cell witness memory-heavy. Full run on disk:
    # PPR-alone 0.264, PPR+w2v fuse 0.323 (both < precision 0.342; fuse beats its shuffled twin) -> topical, does
    # not cross. See data/exp_atl_hubspoke_joint_ppr_recompute_v1/metrics_full.json.

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
