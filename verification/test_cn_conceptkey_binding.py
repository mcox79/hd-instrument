"""verification/test_cn_conceptkey_binding.py -- WITNESS for the concept-key common-noun binding fix.

Scaffold-free: recomputes every headline from source on the FULL GUM modern TEST (odd docs, n=2855
anaphoric common-noun mentions). The fix RE-KEYS the live typed_coref common-noun RESOLUTION gate on a
brain-foundational LEXICAL-CONCEPT lemma (WordNet morphy -- the substrate's standing lemma tool, the ATL
wordform->lemma-concept map) instead of the crude commonnoun_binder.head_lemma regex (an OUR-INVENTION with
a non-alpha->"" false-merge bug + an over-strip bug). GOLD-FREE; the fix is a one-line KEY swap inside the
additive resolution consumer, so it cannot move clustering / coref (no-regress by construction).

Asserts:
  V1  FAITHFUL: resolve_param(crude,string) reproduces the LIVE wire (B._reader_commonnoun_resolution)
      byte-identically -> the crude arm IS the deployed path (so the delta is the fix, nothing else).
  V2  HEADLINE (honest DE-LEAKED floor): the morphy concept-key binding BEATS the redaction-honest
      de-leaked gold floor CI-sep. The de-leaked floor removes ONLY the redaction see-through (GUM fills
      the gold lemma of a redacted "the ____" with the real word -- annotation raw text cannot access);
      it keeps gold lemma quality on every visible word. This is the strongest floor computable from raw text.
  V3  FAIR same-regime: the morphy binding BEATS the morphy string-identity floor CI-sep (the binding adds
      over string-identity IN THE SAME KEY REGIME -- it is not just the better key).
  V4  INFO-FREE TWIN loses CI-sep (the type signal in the non-writing bridge is load-bearing).
  V5  STRICT IMPROVEMENT: the morphy key beats the CRUDE key (the current live wire) -- 0.5482 -> ~0.5580.
  V6  HONEST raw-gold parity: vs the RAW (leaky) gold-lemma floor 0.5412 the binding is +~0.017 with a CI
      that INCLUDES 0 -- asserted honestly (the residual is exactly the irreducible redaction leak, quantified
      by the 0.5412 -> ~0.5254 drop when the see-through is removed).
  V7  LOCATED SUB-NEGATIVE: the loose WordNet-synonymy 'concept' gate is BELOW the lemma arm (identity must
      be lemma-tight; type-compatibility belongs in the NON-writing bridge, not the writing identity gate).

Run: .venv/Scripts/python.exe verification/test_cn_conceptkey_binding.py   (exit 0 = fix confirmed).
Glass-box, CPU, numpy + nltk-WordNet, NO external LLM. ASCII.
"""
from __future__ import annotations
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("PYTHONHASHSEED", "0")
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import experiments.exp_cn_conceptkey_binding_v1 as E


def _check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    return 0 if cond else 1


def main() -> int:
    n_fail = 0
    r = E.run(smoke=False)
    acc = r["acc"]; P = r["paired"]
    lemma = acc["lemma"]

    n_fail += _check(r["n_faithful_docs"] >= 20,
                     "V1 faithful: resolve_param(crude,string) == live wire on %d docs" % r["n_faithful_docs"])

    dl = P["lemma"]["vs_gold_deleaked_floor"]
    n_fail += _check(dl[3] and dl[1] > 0,
                     "V2 morphy binding %.4f BEATS the DE-LEAKED gold floor %.4f d=%+.4f CI[%+.4f,%+.4f] CI-sep=%s"
                     % (lemma, r["floor_gold_deleaked"], dl[0], dl[1], dl[2], dl[3]))

    fm = P["lemma"]["vs_fair_morphy_floor"]
    n_fail += _check(fm[3] and fm[1] > 0,
                     "V3 morphy binding BEATS the FAIR morphy string-identity floor %.4f d=%+.4f CI-sep=%s"
                     % (r["floor_morphy"], fm[0], fm[3]))

    tw = r["lemma_vs_twin"]
    n_fail += _check(tw[3] and tw[1] > 0,
                     "V4 info-free TWIN loses: lemma vs twin d=%+.4f CI[%+.4f,%+.4f] CI-sep=%s" % tw)

    n_fail += _check(lemma > acc["crude"] + 0.005,
                     "V5 strict improvement over the crude live wire: %.4f > %.4f (+%.4f)"
                     % (lemma, acc["crude"], lemma - acc["crude"]))

    rg = P["lemma"]["vs_gold_lemma_floor_0.5412"]
    n_fail += _check((not rg[3]) and rg[0] > 0 and rg[1] <= 0,
                     "V6 HONEST raw-gold parity: vs raw LEAKY gold floor %.4f d=%+.4f CI[%+.4f,%+.4f] "
                     "CI-sep=%s (residual = redaction leak; de-leak drops the floor %.4f->%.4f)"
                     % (r["floor_gold_lemma"], rg[0], rg[1], rg[2], rg[3],
                        r["floor_gold_lemma"], r["floor_gold_deleaked"]))

    n_fail += _check(acc["concept"] < lemma,
                     "V7 located sub-negative: loose-synonymy concept gate %.4f < lemma %.4f (identity must be "
                     "lemma-tight)" % (acc["concept"], lemma))

    print("\nRESULT  %s -- morphy concept-key binding = %.4f, beats the honest de-leaked floor %.4f CI-sep; "
          "twin loses; strict gain over the crude live wire %.4f."
          % ("all PASS (7/7)" if n_fail == 0 else "%d FAIL" % n_fail,
             lemma, r["floor_gold_deleaked"], acc["crude"]))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
