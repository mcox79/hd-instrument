"""Scaffold-free witness for content_addressable_retrieval_over_a_separated_store (p3).

Runs the REAL experiment arms on a small deterministic cell and asserts the load-bearing relationships,
WITHOUT re-running the full sweep or touching any landed metrics.json. Passes with tracing off.

Asserts:
  (1) GUARD -- the FLAT arm's superposition is bit-equal to hdlab.bundling.bundle and single-item unbind
      is exact -> the baseline IS the live op.
  (2) GUARD -- FHRR similarity Re(conj(a)*b) == real dot of the [Re;Im] stack fed to iterative_attractor
      -> the CA3 match consumes faithful FHRR, not a re-derivation.
  (3) POSITIVE CONTROL -- at the FULL cue (p=0), SEP_CA and HASH both near ceiling -> the DV is valid.
  (4) HEADLINE -- under a PARTIAL cue, content-addressable SEP_CA beats the exact-key HASH route AND the
      naive FLAT store, and clears every info-free twin.
  (5) INFO-FREE TWINS LOSE -- SHUFFLED_KEYS / RANDOM_ROUTE / NO_ADDRESS all collapse toward chance.
  (6) LOAD-BEARING NEGATIVE -- CA3_ON_FLAT ties FLAT_CLEANKEY (you cannot clean your way out of
      superposition; the fix is architecture, not terminal cleanup).

Run: .venv/Scripts/python.exe verification/verify_content_addressable_register_retrieval.py
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

from hdlab import tracing  # noqa: E402
try:
    tracing.disable()
except Exception:
    pass

import exp_content_addressable_register_retrieval_v1 as E  # noqa: E402


def _cell(d, load, p, seed, n_trials, cue_mode="fragment"):
    res, pop = E.run_cell(d, load, 0.0, p, seed, n_trials, cue_mode=cue_mode)
    return {k: res[k]["mean"] for k in res}, 1.0 / pop["V"]


def main():
    print("[witness] (1)+(2) GUARDS via the experiment self-test (bundle bit-equal, FHRR==[Re;Im] dot) ...")
    st = E.run_self_test()   # raises on any guard failure
    print("  self-test guards PASS; chance=%.4f" % st["chance"])

    print("[witness] (3) POSITIVE CONTROL: full cue p=0 -> SEP_CA and HASH near ceiling ...")
    p0, chance = _cell(128, 32, 0.0, 101, 30)
    print("  p=0: SEP_CA=%.3f HASH=%.3f FLAT=%.3f" % (p0["SEP_CA"], p0["HASH_BANK"], p0["FLAT"]))
    assert p0["SEP_CA"] >= 0.95, "SEP_CA not at ceiling at full cue: %.3f" % p0["SEP_CA"]
    assert p0["HASH_BANK"] >= 0.85, "HASH not near ceiling at full cue: %.3f" % p0["HASH_BANK"]

    print("[witness] (4)+(5)+(6) PARTIAL cue p=0.7 -> SEP_CA beats HASH/FLAT, twins collapse, CA3_ON_FLAT ties ...")
    r, chance = _cell(128, 32, 0.7, 101, 40)
    print("  p=0.7: SEP_CA=%.3f HASH=%.3f FLAT=%.3f FLAT_CK=%.3f CA3flat=%.3f | SHUF=%.3f RAND=%.3f NOADDR=%.3f"
          % (r["SEP_CA"], r["HASH_BANK"], r["FLAT"], r["FLAT_CLEANKEY"], r["CA3_ON_FLAT"],
             r["SHUFFLED_KEYS"], r["RANDOM_ROUTE"], r["NO_ADDRESS"]))
    assert r["SEP_CA"] > r["HASH_BANK"] + 0.2, "SEP_CA must beat HASH by a clear margin: %.3f vs %.3f" % (
        r["SEP_CA"], r["HASH_BANK"])
    assert r["SEP_CA"] > r["FLAT"] + 0.2, "SEP_CA must beat naive FLAT: %.3f vs %.3f" % (r["SEP_CA"], r["FLAT"])
    strongest_twin = max(r["SHUFFLED_KEYS"], r["RANDOM_ROUTE"], r["NO_ADDRESS"])
    assert strongest_twin < 0.15, "an info-free twin did not collapse: %.3f" % strongest_twin
    assert r["SEP_CA"] > strongest_twin + 0.3, "SEP_CA must clear the strongest twin CI-separated-ish"
    # load-bearing negative: CA3 settle on the flat readback does NOT beat argmax cleanup on it.
    assert r["CA3_ON_FLAT"] <= r["FLAT_CLEANKEY"] + 0.05, (
        "CA3_ON_FLAT should TIE FLAT_CLEANKEY (no cleaning out of superposition): %.3f vs %.3f"
        % (r["CA3_ON_FLAT"], r["FLAT_CLEANKEY"]))
    # separation lever isolated: SEP_CA beats FLAT_CLEANKEY (same key-cleanup, but crosstalk-free read)
    assert r["SEP_CA"] > r["FLAT_CLEANKEY"] + 0.2, (
        "value-separation lever absent: SEP_CA %.3f not > FLAT_CLEANKEY %.3f" % (r["SEP_CA"], r["FLAT_CLEANKEY"]))

    print("[witness] (7) DEEPER DRILL: additive multi-feature retrieval (Lewis-Vasishth) avoids the "
          "multiplicative composite's UNPHYSICAL collapse under an INTERFERENCE cue (near-orthogonal "
          "regime; graded-similarity fan effect is brain-correct, see SOLVED finding 9) ...")
    import exp_feature_cue_retrieval_drill_v1 as D  # noqa: E402
    full = D.run_cell(128, 32, {"entity": 8, "event": 8, "role": 4}, 0, "drop", 7, 6)
    interf = D.run_cell(128, 32, {"entity": 8, "event": 8, "role": 4}, 1, "interference", 7, 6)
    print("  full-cue: COMP=%.3f FEAT=%.3f | 1-interference: COMP=%.3f FEAT=%.3f FAN=%.3f"
          % (full["COMPOSITE_MATCH"]["mean"], full["FEATURE_ACT"]["mean"],
             interf["COMPOSITE_MATCH"]["mean"], interf["FEATURE_ACT"]["mean"], interf["FEATURE_ACT_FAN"]["mean"]))
    assert full["COMPOSITE_MATCH"]["mean"] > 0.9 and full["FEATURE_ACT"]["mean"] > 0.9, "both tie at full cue"
    assert interf["COMPOSITE_MATCH"]["mean"] < 0.15, "composite must COLLAPSE under interference (the fan-effect failure)"
    assert interf["FEATURE_ACT"]["mean"] > interf["COMPOSITE_MATCH"]["mean"] + 0.2, (
        "additive feature-activation must beat the composite under interference: %.3f vs %.3f"
        % (interf["FEATURE_ACT"]["mean"], interf["COMPOSITE_MATCH"]["mean"]))

    print("[witness] (8) REAL-GROUNDED drill: with the substrate's own grounded meaning vectors (real graded "
          "similarity), additive and composite mostly TIE -- finding 8 deflated, additive still safe ...")
    import exp_grounded_feature_retrieval_drill_v1 as GD  # noqa: E402
    gclean, _ = GD.run_cell(48, "clean", 101, 4)
    gsim, _ = GD.run_cell(48, "similar", 101, 4)
    print("  grounded clean: COMP=%.3f FEAT=%.3f | similar-interference: COMP=%.3f FEAT=%.3f"
          % (gclean["COMPOSITE_MATCH"]["mean"], gclean["FEATURE_ACT"]["mean"],
             gsim["COMPOSITE_MATCH"]["mean"], gsim["FEATURE_ACT"]["mean"]))
    assert gclean["FEATURE_ACT"]["mean"] > 0.9 and gclean["COMPOSITE_MATCH"]["mean"] > 0.9, "grounded clue must recover"
    assert GD.grounded_cos("dog", "cat") > GD.grounded_cos("dog", "hammer"), "real grounded structure wrong"
    # additive never catastrophically WORSE than composite (the safety property), on real features
    assert gsim["FEATURE_ACT"]["mean"] >= gsim["COMPOSITE_MATCH"]["mean"] - 0.05, "additive should not be worse"

    print("[witness] ALL PASS (8/8): guards + positive control + headline dissociation + twins + "
          "load-bearing negative + additive-vs-composite drill + real-grounded deflation drill")


if __name__ == "__main__":
    main()
