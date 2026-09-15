"""SCAFFOLD-FREE WITNESS for wire_the_causation_typer_into_the_live_reader.

Recomputes every headline from SOURCE: it builds the WiredCausationReader + the gold + the floors + the
bootstrap FRESH (via the cell's run()/run_precision()/byte_identical_when_off()), never trusting a landed
metrics.json. Run:
    .venv/Scripts/python.exe verification/test_wire_causation_typer_organ.py

Witnesses:
  W1  default-OFF is byte-identical to the stock reader's causal_links on a real LitBank doc (landing invariant)
  W2  with the flag ON the within-clause detector FIRES end-to-end on real LitBank narrative (>=1 typed link)
  W3  AUTO-extraction 3-way (CAUSE/ENABLE/PREVENT) beats the majority-CAUSE floor CI-separated
  W4  AUTO beats the info-free force-class-SHUFFLE twin CI-separated (p95)
  W5  PREVENT positive control: AUTO types prevented (never-happened) endstates the majority-CAUSE floor scores 0
  W6  given-extraction is an upper bound the typer clears, and AUTO recovers most of it (extraction is not fatal)
  W7  PRECISION: on polysemous NON-force uses the pipeline abstains (does NOT assert a force type) for a majority
  W8  the letting/periphrastic construction is EXTRACTED (patient = the complement-clause subject; a NEW front-end)
  W9  gate_mode is load-bearing: domain-general force typing (force) beats the physical-only gate on this task
  W10 CONSTRUCTION GENERALIZATION: the SAME force type transfers across resultative / caused-motion /
      make-periphrastic constructions (manner verbs; the construction supplies the type) -- WITH > WITHOUT
  W11 INCHOATIVE precision: a spontaneous change of state (no affector) does NOT fabricate an external causer
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_wire_causation_typer_live_reader_v1 as W

_PASS = 0
_FAIL = 0


def check(name, cond, detail=""):
    global _PASS, _FAIL
    tag = "PASS" if cond else "FAIL"
    _PASS += int(bool(cond))
    _FAIL += int(not cond)
    print(f"[{tag}] {name}" + (f"  ::  {detail}" if detail else ""))


def main():
    import spacy
    nlp = spacy.load("en_core_web_sm")
    gold = W._load_gold()
    prim = W.run(gold, nlp, use_gate=True, role_source="parse", gate_mode="force")
    phys = W.run(gold, nlp, use_gate=True, role_source="parse", gate_mode="physical_only")
    off = W.byte_identical_when_off(nlp)
    prec = W.run_precision(W._load_notforce_gold(), nlp, use_gate=True)

    # W1 -- default-off byte-identical
    check("W1 default-off byte-identical to stock on real LitBank",
          off.get("ran") and off.get("byte_identical_off") is True,
          f"doc={off.get('doc')} stock_links={off.get('n_stock_links')}")

    # W2 -- the detector fires end-to-end on real narrative
    check("W2 within-clause detector fires end-to-end on real LitBank", off.get("n_real_typed_on", 0) >= 1,
          f"{off.get('n_real_typed_on')} typed links {off.get('type_dist_on')} on {off.get('doc')}")

    # W3 -- AUTO beats majority-CAUSE CI-separated
    a, m = prim["auto"], prim["majority_cause_floor"]
    check("W3 AUTO 3-way > majority-CAUSE floor (CI-separated)", a["lo"] > m["hi"] and prim["beats_majority_ci"],
          f"AUTO {a['acc']:.3f}[{a['lo']:.3f},{a['hi']:.3f}] > majority {m['acc']:.3f}[..,{m['hi']:.3f}] "
          f"(margin {a['lo']-m['hi']:+.3f})")

    # W4 -- AUTO beats the info-free twin CI-separated
    check("W4 AUTO > force-class-shuffle info-free twin (CI-sep)", a["lo"] > prim["twin_p95"] and prim["beats_twin"],
          f"AUTO lo {a['lo']:.3f} > twin p95 {prim['twin_p95']:.3f} (twin mean {prim['twin_mean']:.3f})")

    # W5 -- PREVENT positive control (only force dynamics represents a prevented endstate)
    pc = prim["prevent_control"]
    check("W5 PREVENT positive control (majority-CAUSE cannot represent a prevented endstate)",
          pc["auto_correct"] > pc["majority_correct"] and pc["majority_correct"] == 0 and pc["n"] >= 5,
          f"AUTO {pc['auto_correct']}/{pc['n']} vs majority {pc['majority_correct']}/{pc['n']}")

    # W6 -- given-extraction upper bound clears majority AND auto recovers most of it
    g = prim["given"]
    check("W6 given-extraction UB clears majority; AUTO recovers >=0.9 of it",
          g["acc"] > m["hi"] and a["acc"] >= 0.9 * g["acc"],
          f"given {g['acc']:.3f} (UB); AUTO {a['acc']:.3f} = {a['acc']/g['acc']:.2f} of UB; extraction verb "
          f"{prim['extraction_verb_acc']:.3f}")

    # W7 -- precision on NOT_FORCE polysemy (abstain for a majority)
    check("W7 precision: abstains on polysemous non-force uses (majority)", prec["abstain_rate"] >= 0.6,
          f"NOT_FORCE abstain {prec['n_correct']}/{prec['n']} = {prec['abstain_rate']:.3f} "
          f"(residual = hortative-let, the named WSD target)")

    # W8 -- the letting/periphrastic construction is extracted (patient = complement subject)
    lex = W.build_force_lexicon()
    reader = W.WiredCausationReader(gaz={}, causation_typed=True, nlp=nlp, lexicon=lex, gate_mode="force")
    links = reader._read_causation_typed(
        [["The", "guard", "let", "the", "visitors", "into", "the", "lobby", "."]])
    letting = [l for l in links if l.verb == "let"]
    check("W8 letting/periphrastic construction extracted (causee=complement subject)",
          bool(letting) and letting[0].ctype == "ENABLE" and letting[0].patient == "visitors",
          f"let -> {letting[0].ctype if letting else 'NONE'} patient={letting[0].patient if letting else '-'}")

    # W9 -- gate_mode is load-bearing (domain-general typing beats physical-only)
    check("W9 domain-general force typing > physical-only gate (gate_mode load-bearing)",
          prim["auto"]["acc"] > phys["auto"]["acc"],
          f"force {prim['auto']['acc']:.3f} vs physical_only {phys['auto']['acc']:.3f}")

    # W10 -- construction generalization: the same type transfers across constructions (WITH > WITHOUT)
    cg = W.run_construction_generalization(nlp)
    pcn = cg["per_construction"]
    all_cons_ok = all(pcn[c]["acc"] >= 0.75 for c in ("resultative", "caused_motion", "periphrastic"))
    check("W10 construction generalization (resultative/caused-motion/make all clear; WITH > WITHOUT)",
          all_cons_ok and cg["overall_with"] > cg["overall_without"],
          f"per {[(c, pcn[c]['acc']) for c in pcn]}; WITH {cg['overall_with']:.3f} > WITHOUT {cg['overall_without']:.3f}")

    # W11 -- inchoative precision: a spontaneous change does not fabricate an external causer
    check("W11 inchoative precision (no fabricated causer on spontaneous change)",
          cg["inchoative_precision"] >= 0.75,
          f"no-false-causer rate {cg['inchoative_precision']:.3f}")

    # W12 -- FORCE-EVENT gate: the 3-leg argument vote reduces open-text over-fire (the headline recall,
    # W3, holds WITH the gate on by default). Argument constraint-satisfaction, not verb-sense classification.
    ot = W.run_open_text_scan(nlp)
    check("W12 force-event gate reduces open-text over-fire (recall held: see W3)",
          ot.get("ran") and ot["over_fire_reduction"] > 0 and ot["gate_on"]["n_links"] < ot["gate_off"]["n_links"],
          f"open-text links gate_off {ot['gate_off']['n_links']} -> gate_on {ot['gate_on']['n_links']} "
          f"(-{ot['over_fire_reduction']}); headline AUTO {prim['auto']['acc']:.3f} with gate on")

    print(f"\n==== {_PASS}/{_PASS + _FAIL} PASS ====")
    return _FAIL == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
