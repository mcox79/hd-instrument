"""Scaffold-free WITNESS for the force-dynamic reader's LITERALNESS gate.
   problem: the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate

Recomputes the headline from source (no cached metrics trusted):
  1. The gate SPLITS literal-vs-figurative minimal pairs the un-gated reader cannot (positive control).
  2. On the FROZEN modern gold (150 clauses, UD-EWT+MCScript2) the GATED force-dynamic reader beats the
     FIRE_ANY floor (fire on any physical-verb lemma == base rate) on FIRE-PRECISION, CI-separated (paired).
  3. The info-free TWIN (shuffled sense + permuted concreteness, matched fire rate) LOSES CI-separated.
  4. RECALL stays high (>= 0.85) -- the gate does not collapse the capability.
  5. Concreteness generalizes via WordNet IS-A (a NOVEL abstract noun vetoes; a novel physical one does not).

Run: .venv/Scripts/python.exe verification/test_literalness_gate_organ.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import spacy  # noqa: E402
from experiments._literalness_gate import LiteralnessGate, concreteness_score  # noqa: E402
import experiments.exp_literalness_gate_v1 as EXP  # noqa: E402


def main():
    checks = []
    nlp = spacy.load("en_core_web_sm")
    gate = LiteralnessGate(nlp=nlp)

    # 1. positive control: SAME verb, literal (engage) vs conventional-figurative (abstain)
    pairs = [
        ("The branch broke under the weight .", "break", "weight", "branch", [], True),
        ("The news broke that morning .", "break", "", "news", [], False),
        ("I cut the thick rope with a knife .", "cut", "i", "rope", [], True),
        ("The company cut funding for the program .", "cut", "company", "funding", [], False),
        ("Birth rates increased the poverty .", "increase", "rates", "poverty", [], False),
        ("I poured the water into the glass .", "pour", "i", "water", ["into"], True),
    ]
    pc_ok = 0
    for st, lem, aff, pat, ctx, exp in pairs:
        doc = nlp(st); sent = list(doc.sents)[0]
        vt = next((t for t in sent if t.lemma_.lower() == lem and t.pos_ == "VERB"), None) \
            or next((t for t in sent if t.lemma_.lower() == lem), None)
        got = gate.assess(sent, vt, aff, pat, ctx, use_oblique=True)["engage"] if vt else False
        pc_ok += int(got == exp)
    checks.append((f"positive control: gate splits literal/figurative minimal pairs {pc_ok}/{len(pairs)}",
                   pc_ok >= len(pairs) - 1))

    # 5. concreteness generalizes via WordNet IS-A to NOVEL nouns (not a word list)
    novel_abstract = all(concreteness_score(n) <= 0.2 for n in ["nostalgia", "bureaucracy", "connotation"])
    novel_physical = all(concreteness_score(n) >= 0.7 for n in ["boulder", "kettle", "trolley"])
    checks.append(("concreteness IS-A generalizes: novel abstract nouns veto, novel physical do not",
                   novel_abstract and novel_physical))

    # 2-4. recompute the gold headline (small bootstrap for speed)
    m = EXP.run(nlp=nlp, boot=400)
    prec = m["precision"]
    d = m["paired_precision_delta"]
    checks.append((f"GATED precision {prec['GATED']:.3f} beats FIRE_ANY base rate {prec['FIRE_ANY']:.3f} "
                   f"CI-separated (paired delta lo {d['GATED_minus_FIRE_ANY'][1]:.3f} > 0)",
                   d["GATED_minus_FIRE_ANY"][1] > 0))
    checks.append((f"info-free TWIN {prec['TWIN']:.3f} LOSES CI-separated "
                   f"(paired delta lo {d['GATED_minus_TWIN'][1]:.3f} > 0)", d["GATED_minus_TWIN"][1] > 0))
    checks.append((f"RECALL stays high {m['recall']['GATED']:.3f} (>= 0.85 -- capability not collapsed)",
                   m["recall"]["GATED"] >= 0.85))

    # 6. HELD-OUT generalization to an UNSEEN genre (RACE essay prose), ZERO params re-tuned: the gain is
    #    DIRECTIONAL (>0) and the info-free twin LOSES -- honest (the margin is not CI-separated on essay prose;
    #    that is the mapped concrete-role-figurative boundary, recorded in SOLVED.md).
    import experiments.exp_literalness_gate_heldout_race_v1 as HO
    h = HO.run(nlp=nlp, boot=400)
    checks.append((f"held-out RACE generalization (n={h['n']}, unseen essay genre): gain CI-separated "
                   f"(+{h['paired_delta_GATED_minus_FIRE_ANY'][0]:.3f} "
                   f"[{h['paired_delta_GATED_minus_FIRE_ANY'][1]:.3f},{h['paired_delta_GATED_minus_FIRE_ANY'][2]:.3f}]) "
                   f"and twin LOSES (+{h['paired_delta_GATED_minus_TWIN'][0]:.3f})",
                   h["paired_delta_GATED_minus_FIRE_ANY"][1] > 0 and h["paired_delta_GATED_minus_TWIN"][0] > 0))

    # 7. DOWNSTREAM / END-TO-END: the gate actually cuts the reader's figurative mislabels (the brief's point).
    import experiments.exp_literalness_gate_endtoend_v1 as E2E
    e = E2E.run(nlp=nlp)
    a = e["aggregate_150"]
    checks.append((f"end-to-end: gate cuts the reader's false physical-type rate "
                   f"{a['false_physical_type_rate_UNGATED']:.2f}->{a['false_physical_type_rate_GATED']:.2f} "
                   f"({a['reduction_pct']:.0f}% fewer figurative mislabels) keeping literal coverage "
                   f"{a['literal_coverage_GATED']:.2f}",
                   a["false_physical_type_rate_GATED"] < a["false_physical_type_rate_UNGATED"] - 0.2
                   and a["literal_coverage_GATED"] >= 0.80))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS  (glass-box literalness gate: concreteness/selectional over "
          f"force roles + Talmy Ground + stored-unit vobj-idiom + attachment; no LLM)")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
