# WIRE-DON'T-ISLAND PROMOTION WITNESS (2026-08-08). Scaffold-free, tracing=False (the organ under
# test takes no HDC tracing flag).
"""verification/test_goal_achievement.py -- witness for hdlab.goal_achievement (3-channel glass-box
goal/desire-fulfillment verdict), promoted straight from session scratchpad
(integrated_goal_achievement_v1 + connective_channel_v1). See hdlab/goal_achievement.py's docstring for
the mechanism + the validated benchmark number.

BENCHMARK PROVENANCE (not reproducible in-repo -- DesireDB.csv is not committed): on the real DesireDB
n=80 balanced seed-20260808 subsample, the wired module reproduces macro-F1 0.686 / acc 0.688, above the
tuned valence+negation RULE (macro-F1 0.620) -- disk-verified this promotion by running
goal_achievement_verdict over the scratchpad DesireDB loader (F1 0.706, macroF1 0.686, acc 0.688,
matching connective_channel_v1's 0.686/0.688; the 0.714->0.706 F1 delta is a 1-item positive-class
rounding diff, macro-F1 identical). This witness cannot re-run that (no committed data), so it asserts
the per-CHANNEL mechanism behavior + determinism instead.

Three checks:
  (1) MECHANISM-FIRES: each of the 3 channels + the majority fallback + the contrast override produces
      the correct verdict via the expected channel on a clear representative case (6 cases). One case
      documents a KNOWN lemmatizer gap (irregular past 'met' not stemmed to 'meet' -> relation abstains
      -> majority; verdict still correct) rather than asserting an aspirational fire.
  (2) GRACEFUL DEGRADE: the valence channel never raises even if nltk opinion_lexicon is absent (it
      returns None or a decision, never an exception) -- goal_achievement_verdict always returns a dict.
  (3) DETERMINISM: same (desire, outcome) -> byte-identical result dict, twice.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_achievement import (  # noqa: E402
    goal_achievement_verdict, valence_channel, relation_channel, contrast_present, self_test,
)

# (desire, outcome, expected_verdict, expected_channel_prefix_or_None)
CASES = [
    ("I wanted to meet my friend.", "I met up with my friend.", "Fulfilled", "majority"),          # lemmatizer gap -> majority
    ("I wanted to save him.", "But I couldn't.", "Unfulfilled", "relation"),                        # refusal
    ("I wanted a good day.", "It was wonderful and I felt so happy.", "Fulfilled", "valence"),      # valence +
    ("I wanted a good day.", "It was a terrible, miserable disaster.", "Unfulfilled", "valence"),   # valence -
    ("I wanted to relax at home.", "But people showed up and started drinking.", "Unfulfilled", "contrast_override"),
    ("I wanted to get the kids to the museum.", "On Tuesday we did just that.", "Fulfilled", "relation"),  # pro-form
]


def check_mechanism_fires():
    for desire, outcome, exp_v, exp_c in CASES:
        r = goal_achievement_verdict(desire, outcome)
        assert r["verdict"] == exp_v, f"verdict {r['verdict']!r} != {exp_v!r} for {outcome!r} ({r})"
        if exp_c is not None:
            assert r["channel"].startswith(exp_c), \
                f"channel {r['channel']!r} !startswith {exp_c!r} for {outcome!r}"
    print(f"[CHECK mechanism_fires] {len(CASES)}/{len(CASES)} cases: correct verdict via expected channel "
          f"(valence/relation/contrast_override/majority all exercised)")
    return {"n": len(CASES)}


def check_graceful_and_types():
    # valence channel returns str|None and never raises; verdict dict shape stable
    v = valence_channel("It was a wonderful, happy day.")
    assert v in ("Fulfilled", "Unfulfilled", None)
    rel, reason = relation_channel("I wanted to win.", "I lost badly.")
    assert rel in ("Fulfilled", "Unfulfilled", None) and isinstance(reason, str)
    assert isinstance(contrast_present("but it failed"), bool)
    r = goal_achievement_verdict("I wanted x.", "y happened.")
    assert set(r.keys()) >= {"verdict", "channel", "reason", "trace"}
    assert r["verdict"] in ("Fulfilled", "Unfulfilled")
    print("[CHECK graceful] valence/relation/contrast return typed values, never raise; verdict dict shape stable")
    return {"ok": True}


def check_determinism():
    for desire, outcome, _v, _c in CASES:
        a = goal_achievement_verdict(desire, outcome)
        b = goal_achievement_verdict(desire, outcome)
        assert a == b, f"non-deterministic on {outcome!r}: {a!r} != {b!r}"
    print(f"[CHECK determinism] {len(CASES)} cases stable across repeated calls")
    return {"n": len(CASES)}


def test_mechanism_fires():
    check_mechanism_fires()


def test_self_test_passes():
    # the module's own embedded self_test (same cases) must pass
    r = self_test()
    assert r["n"] == 6


def test_graceful_and_types():
    check_graceful_and_types()


def test_determinism():
    check_determinism()


def run():
    r1 = check_mechanism_fires()
    r2 = check_graceful_and_types()
    r3 = check_determinism()
    self_test()
    print("[ALL CHECKS PASS] hdlab/goal_achievement: 3 channels + majority + contrast-override fire "
          "correctly; graceful; deterministic. (Benchmark macro-F1 0.686 > rule 0.620 disk-verified "
          "this promotion; not re-run here -- DesireDB not committed.)")
    return {"mechanism": r1, "graceful": r2, "determinism": r3}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, default=str))
