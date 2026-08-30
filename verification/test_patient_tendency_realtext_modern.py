"""Scaffold-free witness for the MODERN real-text serve of the patient-tendency estimator.
   problem: causation_typing_needs_a_patient_tendency_estimator

Runs the frozen hand-adjudicated MODERN serve (verbatim MCScript2/UD-EWT, extraction given) and asserts
the load-bearing claims -- on MODERN text (NOT McGuffey; avoids the ~200-year age confound):
  1. The estimator FIRES on modern inflected prose (lemmatization) and, where it fires on genuine
     tendency cases, is highly accurate; it beats the lexicon-only floor.
  2. It reads in-sentence property ADJECTIVES ("heavy" door -> CAUSE) incl. NEGATION ("not very heavy"
     -> ENABLE), and gravity ("slid down" -> ENABLE), and disposition ("ball rolled" -> ENABLE).
  3. On DIRECT AGENTIVE manipulation the tendency mechanism correctly DEFERS (does not impose a
     tendency-based type from a spurious cue) -- the honest behavior.

Run: .venv/Scripts/python.exe verification/test_patient_tendency_realtext_modern.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import experiments.exp_patient_tendency_realtext_modern_v1 as R  # noqa: E402
from experiments._force_dynamics_lexicon import build_force_lexicon  # noqa: E402


def main():
    checks = []
    try:
        R.self_test()
        checks.append(("serve self-test: ball rolled->ENABLE, heavy door->CAUSE, agentive 'lifted'->defers", True))
    except AssertionError as e:
        checks.append((f"serve self-test: {e}", False))

    lex = build_force_lexicon()
    rows = R._score(lex)
    m = R._metrics(rows)

    checks.append((f"MODERN OUTPUT accuracy on tendency cases {m['output_accuracy_on_tendency']:.2f} "
                   f"({m['n_output_correct']}/{m['n_tendency']}) -- correct on ALL tendency cases",
                   m["output_accuracy_on_tendency"] >= 0.99))
    checks.append((f"tendency mechanism fires accurately: {m['accuracy_where_fired']:.2f} where it fires "
                   f"({m['n_fired_correct']}/{m['tendency_fired']})",
                   m["accuracy_where_fired"] >= 0.99 and m["tendency_fired"] >= 5))
    checks.append((f"beats lexicon-only on modern tendency cases: output-correct {m['n_output_correct']} > "
                   f"lexicon-only {m['lexicon_only_correct_on_tendency']}",
                   m["n_output_correct"] > m["lexicon_only_correct_on_tendency"]))
    # the DERIVED causative-inchoative gate now types the letting case 'drain' (was a hand-list miss)
    drain = next(r for r in rows if r["verb"] == "drain")
    checks.append((f"DERIVED verb-gate (causative-inchoative) types the LETTING case: plug/drain/water -> "
                   f"{drain['est']} (ENABLE via letting; 'drain' now gated)", drain["est"] == "ENABLE"))
    checks.append((f"correctly DEFERS on agentive manipulation: {m['agentive_abstained_correctly']}/"
                   f"{m['n_agentive_abstain_gold']} (rate {m['agentive_abstain_rate']:.2f})",
                   m["agentive_abstain_rate"] >= 0.99))

    # specific brain-foundational behaviors on real sentences
    def find(pat, verb):
        return next(r for r in rows if r["patient"] == pat and r["verb"] == verb)
    door = find("door", "opened"); tbl = find("table", "pushed")
    checks.append((f"ADJECTIVE read on real text: 'heavy' door -> {door['est']} (CAUSE)",
                   door["est"] == "CAUSE" and door["fired"]))
    checks.append((f"NEGATION on real text: 'not very heavy' table -> {tbl['est']} (ENABLE)",
                   tbl["est"] == "ENABLE" and tbl["fired"]))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS  (MODERN real-text point estimate; full rows in "
          f"data/exp_patient_tendency_realtext_modern_v1/metrics.json)")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
