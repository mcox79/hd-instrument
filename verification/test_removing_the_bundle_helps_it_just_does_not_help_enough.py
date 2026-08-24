"""Removing the bundle BEATS the flat bag CI-separated. "Not the bottleneck" is not "costs nothing".

WHERE THIS COMES FROM. Reviewing the priority-3 solver submission
(`the_bundle_destroys_meaning_but_replacing_it_hurts`, status SOLVED, 2026-08-23). Its re-verify
passes and its central discovery is real and valuable:

    THE STRING FLOOR THAT HAS BEEN BEATING US ~2:1 IS MOSTLY MORPHOLOGY.
    Strip stem-sharing pairs out of the WordNet gold and the spelling control collapses
    0.0867 -> 0.0193, which OVERLAPS its own info-free shuffled twin (0.0173). On
    leakage-free gold the distributional arms win CI-separated. That is a genuine result
    and it retires a floor that had been steering the whole thread.

**BUT ITS HEADLINE IS "THE BUNDLING IS NOT THE c3 BOTTLENECK", AND ITS OWN PAIRED BOOTSTRAP SAYS
REMOVING THE BUNDLE WINS.** From the same metrics.json, full gold, n=4000, 5000x paired bootstrap:

    d_RAW_COOC_minus_A1_BASE = +0.0125, CI [+0.0057, +0.0195]   <- EXCLUDES ZERO

`RAW_COOC` is explicit per-context co-occurrence counts with ZERO superposition; `A1_BASE` is the
shipped flat bag. So deleting the bundle entirely is worth **+0.0125, about 26% of the flat bag's
own score (0.0480)**, and it is CI-separated.

**HOW BOTH THINGS ARE TRUE.** The submission's argument was: removing the bundle still loses to the
spelling floor, therefore bundling is not what limits c3. The first half is correct on full gold
(0.0605 vs 0.0867). **The trouble is that the SAME submission then demolishes that comparator as
morphological leakage.** Against the floor it demolished, the argument does not carry; against the
actual shipped system, removing the bundle WINS.

    THE ACCURATE STATEMENT: removing the bundle HELPS, CI-separated, and it does NOT help
    ENOUGH to clear the task. That is a different claim from "bundling costs nothing", and
    only one of them tells a future reader to keep looking at the representation.

WHY THIS MATTERS FOR THE BUILD. "Not the bottleneck" reads as "stop working on it." A CI-separated
+0.0125 from deleting superposition, on the task where two replacement operators previously LOST,
says the opposite: the cost is real and measurable, and the two refuted arms (STRUCTURE_HURTS,
CONJUNCTIVE_HURTS) were the wrong replacements rather than evidence of no cost.

NOT ESTABLISHED, AND DO NOT LET THIS TRAVEL FURTHER THAN IT GOES:
  * +0.0125 is small in absolute terms and does not approach clearing the task.
  * The strip-gold pair `RAW_COOC` vs `A1_BASE` was NOT computed as a paired delta by the cell;
    only the point estimates are available there (0.0582 vs 0.0459, consistent in sign and size).
    This test asserts the FULL-gold paired delta, which the cell did compute.
  * `RAW_COOC` is an explicit count table, not a deployable representation. It bounds what the
    bundle costs; it is not a proposal to ship.

    .venv/Scripts/python.exe verification/test_removing_the_bundle_helps_it_just_does_not_help_enough.py
"""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS = os.path.join(REPO, "data", "exp_c3_surprise_weighted_vs_bundling_v1", "metrics.json")


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-60s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    if not os.path.exists(METRICS):
        print("[witness] FAIL metrics missing: %s" % METRICS)
        raise SystemExit(1)
    with io.open(METRICS, encoding="utf-8") as fh:
        m = json.load(fh)

    chk("this is the FULL run, not a smoke", m.get("run_mode") == "full",
        "run_mode=%r n_items=%s anchors=%s" % (m.get("run_mode"), m.get("n_items_full"),
                                               m.get("n_anchors")))

    full_ci = m["full"]["bootstrap"]["arm_acc_ci"]
    strip_ci = m["strip"]["bootstrap"]["arm_acc_ci"]
    deltas = m["full"]["bootstrap"]["deltas"]

    # 1. THE SUBMISSION'S REAL FINDING, WHICH THIS REVIEW UPHOLDS.
    s_full = full_ci["A5_STRINGCTRL"]["acc"]
    s_strip = strip_ci["A5_STRINGCTRL"]["acc"]
    chk("the spelling floor COLLAPSES once stem-sharing gold is removed",
        s_strip < 0.3 * s_full,
        "%.4f -> %.4f (%.0f%% of it was morphology)" % (s_full, s_strip,
                                                        100.0 * (1 - s_strip / s_full)))
    shuf = strip_ci["SHUF_COOC"]
    chk("and on leakage-free gold it OVERLAPS its own info-free twin",
        strip_ci["A5_STRINGCTRL"]["ci_lo"] < shuf["ci_hi"],
        "string [%.4f,%.4f] vs shuffled [%.4f,%.4f]"
        % (strip_ci["A5_STRINGCTRL"]["ci_lo"], strip_ci["A5_STRINGCTRL"]["ci_hi"],
           shuf["ci_lo"], shuf["ci_hi"]))

    # 2. THE PART ITS HEADLINE CONTRADICTS.
    d = deltas["d_RAW_COOC_minus_A1_BASE"]
    chk("removing the bundle BEATS the flat bag, CI-separated",
        d["ci_lo"] > 0,
        "delta %+.4f CI[%+.4f,%+.4f] -- excludes zero" % (d["delta"], d["ci_lo"], d["ci_hi"]))
    base = full_ci["A1_BASE"]["acc"]
    chk("and the gain is a large FRACTION of the flat bag's own score",
        d["delta"] > 0.15 * base,
        "%+.4f is %.0f%% of A1_BASE %.4f" % (d["delta"], 100.0 * d["delta"] / base, base))

    # 3. AND THE HALF OF THE SUBMISSION'S ARGUMENT THAT IS CORRECT -- both must hold at once,
    #    or this review is just swapping one over-reading for another.
    d2 = deltas["d_RAW_COOC_minus_A5_STRINGCTRL"]
    chk("it STILL loses to the (leaky) spelling floor on full gold",
        d2["ci_hi"] < 0,
        "delta %+.4f CI[%+.4f,%+.4f] -- so 'does not help ENOUGH' is also true"
        % (d2["delta"], d2["ci_lo"], d2["ci_hi"]))

    # NEGATIVE CONTROL: the info-free arms must lose to everything, or the metric is degenerate
    # in this regime and no delta above means anything.
    for arm in ("RANDOM", "SHUF_COOC"):
        chk("NEGATIVE CONTROL: %s loses to the flat bag" % arm,
            full_ci[arm]["ci_hi"] < full_ci["A1_BASE"]["ci_lo"],
            "%s %.4f vs A1_BASE %.4f" % (arm, full_ci[arm]["acc"], base))

    print()
    print("[witness] READ THIS AS: the bundle costs a real, CI-separated amount, and removing it")
    print("[witness] is not sufficient to clear the task. NOT as: bundling is free.")
    print("[witness] RESULT: %s" % ("ALL WITNESS CHECKS PASS" if ok else "FAILED"))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()

# ---- PYTEST ENTRY POINT ------------------------------------------------------------------
# WIRED 2026-08-23. WITHOUT THIS THE FILE IS ISLANDED: it is named test_*.py and sits in
# verification/, so it LOOKS like it is in the certification gate, but it defines no test_
# function, so pytest collects ZERO tests from it and run_certification.py never executes it.
# That is the same shape as the hazard run_certification.py documents in its own comment (a
# script-style file under a test_ name), arriving from the opposite direction: that one aborted
# the suite loudly, this one is skipped silently. A witness the gate does not run is a witness
# nobody runs.
# This reads only a metrics.json, so it costs milliseconds and is safe to add to the gate.
def test_removing_the_bundle_helps_but_not_enough():
    try:
        main()
    except SystemExit as exc:
        assert exc.code == 0, "witness FAILED (exit %r) -- run the file directly for the detail" % (exc.code,)
