"""Scaffold-free witness for BRAIN-FOUNDATIONAL GENERALIZATION of the patient-tendency estimator.
   problem: causation_typing_needs_a_patient_tendency_estimator

The brain generalizes force-dynamic causal typing by grounding a word in its CONCEPTUAL FEATURE / image
schema (Talmy; Lakoff; Barsalou grounded simulation) -- NOT a word list. This witness asserts that:
  1. The INCLINED-SURFACE schema is IS-A grounded (WordNet), so it GENERALIZES to NOVEL grounds a hand-list
     never had (knoll/ravine/escarpment) while a bare particle without a ground ("turn UP the sound") does
     NOT fire -- the particle-vs-path distinction.
  2. On UNFILTERED modern web text (UD-EWT, gold-parse auto-extraction) the estimator is CONSERVATIVE
     (very low fire rate) -- the phrasal-verb over-fires are gone; it does NOT hallucinate tendency.

Run: .venv/Scripts/python.exe verification/test_patient_tendency_generalization.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments._patient_tendency import directional_sign  # noqa: E402
import experiments.exp_patient_tendency_generalization_udewt_v1 as G  # noqa: E402


def main():
    checks = []

    # 1. IS-A grounding generalizes to NOVEL grounds (not in the hand-list) via the inclined-surface schema
    novel = ["knoll", "ravine", "escarpment", "gully", "hillside"]
    novel_fire = all(directional_sign(["down", "the", g]) == 1 for g in novel)
    checks.append((f"IS-A grounding GENERALIZES to novel grounds {novel} (down the <novel> -> +1)", novel_fire))
    # a bare particle with NO spatial ground must NOT fire (particle-vs-path)
    particle_ok = (directional_sign(["up", "sound"]) == 0 and directional_sign(["down"]) == 0
                   and directional_sign(["back"]) == 0)
    checks.append(("particle-vs-path: bare 'up/down/back' with no ground do NOT fire (no phrasal over-fire)",
                   particle_ok))

    # 2. conservative on unfiltered modern web text (no over-fire flood)
    res = G.main()
    fr = res["fire_rate"]
    checks.append((f"CONSERVATIVE on unfiltered UD-EWT web text: fire rate {fr:.3f} "
                   f"({res['fired']}/{res['total_gated_clauses']}) -- no over-fire flood", fr < 0.03))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS  (brain-like generalization: word -> conceptual feature, not "
          f"a word list; residual over-fires are word-sense/attachment = the WSD follow-on)")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
