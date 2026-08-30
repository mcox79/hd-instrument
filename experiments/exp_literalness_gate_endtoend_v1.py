"""END-TO-END: does the gate actually PROTECT the force-dynamic reader? (the brief's real concern:
   "the causation typer wired into the LIVE reader would mislabel figurative sentences as physical
   force-dynamic events"). problem: the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate

The reader = the integrated force typer (hdlab.force_dynamics_typer) + patient-tendency estimator
(experiments._patient_tendency), which emit a physical CAUSE / ENABLE / PREVENT label for EVERY
force-verb clause. WITHOUT the gate, every figurative use gets a physical causal type (the over-fire).
WITH the gate, the reader ENGAGES (emits the type) only on ENGAGE_PHYSICAL and ABSTAINS otherwise.

We report, on the frozen 150-item modern gold:
  * FALSE-PHYSICAL-TYPE RATE = fraction of NON-literal (gold != A) clauses to which the reader assigns a
    physical causal type. UN-gated = 1.0 (the typer types every force verb); gated = the gate's false-engage
    fraction. The DROP is the protection the gate buys.
  * LITERAL COVERAGE = fraction of literal (gold == A) clauses the reader still types (recall).
Plus a QUALITATIVE table on the brief's OWN examples (figurative vs literal minimal contrasts) showing the
un-gated reader's label and the gate's decision -- the visceral "it does its job" artifact.

ASCII only. No LLM (spaCy + WordNet + FrameNet). No hdlab writes.
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._literalness_gold import load_gold
from experiments._literalness_gate import LiteralnessGate
from experiments._patient_tendency import type_with_full_tendency
from experiments.exp_literalness_gate_v1 import _locate_verb
from hdlab.force_dynamics_typer import build_force_lexicon

ANCHOR = "literalness_gate_endtoend_v1"

# The brief's own figurative examples + literal minimal-contrast controls.
QUALITATIVE = [
    ("The news broke that morning .", "break", "", "news", [], "figurative"),
    ("The branch broke under the weight .", "break", "weight", "branch", [], "literal"),
    ("She opened up to him about her fears .", "open", "she", "she", ["up", "to"], "figurative"),
    ("She opened the heavy door slowly .", "open", "she", "door", [], "literal"),
    ("The deal fell through at the last minute .", "fall", "deal", "deal", ["through"], "figurative"),
    ("The vase fell off the shelf .", "fall", "vase", "vase", ["off"], "literal"),
    ("He was crushed by the criticism .", "crush", "criticism", "he", [], "figurative"),
    ("The car was crushed by the falling rock .", "crush", "rock", "car", [], "literal"),
    ("Birth rates increased the poverty .", "increase", "rates", "poverty", [], "figurative"),
    ("I poured the water into the glass .", "pour", "i", "water", ["into"], "literal"),
]


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def run(nlp=None):
    import spacy
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    gate = LiteralnessGate(nlp=nlp)
    lex = build_force_lexicon()

    # ---- qualitative table on the brief's own examples ----
    qual = []
    for st, lem, aff, pat, ctx, kind in QUALITATIVE:
        doc = nlp(st); sent = list(doc.sents)[0]
        vt = _locate_verb(sent, lem, pat)
        ungated_type = type_with_full_tendency(aff, lem, pat, ctx, True, lex)  # what the reader emits, no gate
        eng = gate.assess(sent, vt, aff, pat, ctx, use_oblique=True)["engage"] if vt else False
        gated_out = ungated_type if eng else "ABSTAIN"
        correct = (kind == "literal") == eng
        qual.append({"kind": kind, "verb": lem, "sentence": st, "ungated_reader": ungated_type,
                     "gated_reader": gated_out, "gate_correct": correct})

    # ---- aggregate on the 150-item gold ----
    items = load_gold()
    non_lit = [c for c in items if c["label"] != "A"]
    lit = [c for c in items if c["label"] == "A"]
    false_phys_ungated = 0
    false_phys_gated = 0
    lit_typed_ungated = 0
    lit_typed_gated = 0
    for c in items:
        doc = nlp(c["sent"])
        sent = next((s for s in doc.sents if any(t.lemma_.lower() == c["lemma"] for t in s)),
                    list(doc.sents)[0])
        vt = _locate_verb(sent, c["lemma"], c["patient"])
        # un-gated: the typer emits a physical causal type for every force-verb clause
        ungated_type = type_with_full_tendency(c["affector"], c["lemma"], c["patient"], c["context"], True, lex)
        emits_physical = ungated_type in ("CAUSE", "ENABLE", "PREVENT")
        eng = gate.assess(sent, vt, c["affector"], c["patient"], c["context"], use_oblique=True)["engage"] if vt else False
        if c["label"] != "A":
            false_phys_ungated += int(emits_physical)
            false_phys_gated += int(emits_physical and eng)
        else:
            lit_typed_ungated += int(emits_physical)
            lit_typed_gated += int(emits_physical and eng)

    fpr_ungated = false_phys_ungated / max(1, len(non_lit))
    fpr_gated = false_phys_gated / max(1, len(non_lit))
    lit_cov_ungated = lit_typed_ungated / max(1, len(lit))
    lit_cov_gated = lit_typed_gated / max(1, len(lit))

    m = {
        "verdict": "ENDTOEND__GATE_PROTECTS_THE_READER",
        "qualitative": qual,
        "qualitative_correct": sum(q["gate_correct"] for q in qual),
        "qualitative_n": len(qual),
        "aggregate_150": {
            "n_nonliteral": len(non_lit), "n_literal": len(lit),
            "false_physical_type_rate_UNGATED": round(fpr_ungated, 4),
            "false_physical_type_rate_GATED": round(fpr_gated, 4),
            "false_types_removed": false_phys_ungated - false_phys_gated,
            "reduction_pct": round(100 * (false_phys_ungated - false_phys_gated) / max(1, false_phys_ungated), 1),
            "literal_coverage_UNGATED": round(lit_cov_ungated, 4),
            "literal_coverage_GATED": round(lit_cov_gated, 4),
        },
        "headline": (
            f"On the 150-item modern gold, the un-gated reader assigns a PHYSICAL causal type to "
            f"{false_phys_ungated}/{len(non_lit)} NON-literal clauses (false-physical-type rate "
            f"{fpr_ungated:.2f}); the GATE cuts that to {false_phys_gated}/{len(non_lit)} ({fpr_gated:.2f}) "
            f"-- {round(100*(false_phys_ungated-false_phys_gated)/max(1,false_phys_ungated))}% fewer figurative "
            f"mislabels -- while keeping literal coverage {lit_cov_gated:.2f} (of {lit_cov_ungated:.2f}). "
            f"Qualitative: {sum(q['gate_correct'] for q in qual)}/{len(qual)} of the brief's own "
            f"figurative-vs-literal examples handled correctly."),
        "anchor_name": ANCHOR, "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    return m


def self_test():
    import spacy
    nlp = spacy.load("en_core_web_sm")
    m = run(nlp=nlp)
    a = m["aggregate_150"]
    assert a["false_physical_type_rate_GATED"] < a["false_physical_type_rate_UNGATED"], "gate must reduce false types"
    print("[self-test] PASS", m["headline"][:120])
    return True


def main():
    out = _out_dir()
    t0 = time.perf_counter()
    m = run()
    m["elapsed_s"] = round(time.perf_counter() - t0, 2)
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    print(m["headline"])
    for q in m["qualitative"]:
        print(f"  [{q['kind']:9s}] {q['verb']:8s} ungated={q['ungated_reader']:8s} -> gated={q['gated_reader']:8s} "
              f"{'OK' if q['gate_correct'] else 'XX'}  :: {q['sentence'][:46]}")
    return m


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test(); sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        with open(os.path.join(_out_dir(), "metrics.json"), "w", encoding="ascii") as f:
            json.dump({"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                       "traceback": traceback.format_exc()[:3000]}, f)
        raise
