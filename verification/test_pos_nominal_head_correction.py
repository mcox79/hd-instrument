"""SCAFFOLD-FREE witness for the BF upstream POS fix (experiments/exp_pos_nominal_head_correction_v1.py)
that unblocks harm/help: rare/OOV common nouns mistagged ADJ in DP-head position (medic/intern) are
re-tagged NOUN by the determiner-projects-a-nominal-head constraint + the lexical category prior. Locks:

  W1 CORRECTION: medic/intern (ADJ->NOUN) recovered; nominalized adjectives (the poor/the rich) left ADJ.
  W2 LEXICAL PRIOR IS LOAD-BEARING: on the UD-EWT DP-head-ADJ target population the fix beats the
     info-free random-retag control on recall (and does not worsen precision).
  W3 NO GLOBAL REGRESSION: overall UPOS accuracy does not drop.
  W4 DOWNSTREAM CASCADE: 'blocked the medic from saving the wounded' recovers HELP->HARM (the POS fix
     lets the parser bind the patient + attach the from-clause), and 'A coworker bullied the intern'
     recovers HARM through the REAL reader ONLY when BOTH the POS fix and the harm/help arithmetic are
     live (neither alone -- the 'every component in the chain must be BF' principle).

Run: .venv/Scripts/python.exe verification/test_pos_nominal_head_correction.py
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_pos_nominal_head_correction_v1 as P


def test_pos_nominal_head_correction():
    results = []

    def chk(name, cond, detail=""):
        results.append(cond)
        print(f"  {'ok' if cond else 'XX'}  {name}{('  -- ' + detail) if detail else ''}")

    # 2026-09-12: the DP-head correction is LIVE inside hdlab.pos_tagger.tag() (Bayesian version, pri-7 landing). This
    # witness measures the FIX against the RAW perceptron path, so switch the live default off for the measurement --
    # and first assert (W0) that the live path equals the solver's Bayesian cell on the W1 sentences.
    import hdlab.pos_tagger as PT
    import experiments.exp_pos_bayesian_category_v1 as POSB
    tg = P.tagger()
    w0 = all(list(tg.tag(t, dp_head_correction=True)) == POSB.bayesian_correction(t, list(tg.tag(t, dp_head_correction=False)))
             for t in (["A", "coworker", "bullied", "the", "intern", "."], ["The", "guard", "blocked", "the", "medic", "from", "x", "."],
                       ["We", "help", "the", "poor", "."], ["He", "robs", "the", "rich", "."]))
    chk("W0 LIVE tag() == the Bayesian DP-head correction (landed version) on the W1 sentences", w0)
    PT.DP_HEAD_CORRECTION = False

    # ---- W1 CORRECTION -----------------------------------------------------------------------------
    w1 = True
    for toks, head, want in ((["A", "coworker", "bullied", "the", "intern", "."], "intern", "NOUN"),
                             (["The", "guard", "blocked", "the", "medic", "from", "x", "."], "medic", "NOUN"),
                             (["We", "help", "the", "poor", "."], "poor", "ADJ"),
                             (["He", "robs", "the", "rich", "."], "rich", "ADJ")):
        base = list(tg.tag(toks))   # RAW perceptron path (module default switched off above for this measurement)
        fix = P.nominal_head_correction(toks, base)
        hi = toks.index(head)
        w1 = w1 and fix[hi] == want
    chk("W1 correction: medic/intern -> NOUN; the poor/the rich left ADJ", w1)

    # ---- W2 + W3 UD-EWT: lexical prior beats info-free control; no global regression --------------
    r = P.run(cap=1500)
    fixm = r["udewt_target_population"]["fix"]
    ctrlm = r["udewt_target_population"]["info_free_control"]
    chk("W2 lexical prior load-bearing: target-population recall beats the info-free random-retag control "
        "at no worse precision", fixm["recall"] > ctrlm["recall"]
        and fixm["precision_error"] <= ctrlm["precision_error"],
        f"fix recall={fixm['recall']} pe={fixm['precision_error']} | ctrl recall={ctrlm['recall']} "
        f"pe={ctrlm['precision_error']}")
    ov = r["udewt_overall"]
    chk("W3 no global UPOS regression", ov["acc_fix"] >= ov["acc_base"],
        f"base={ov['acc_base']} fix={ov['acc_fix']}")
    hh = r["harm_help_patient_nouns"]
    chk("W3b harm/help patient-role nouns: the fix recovers mistagged nouns (medic/intern) NOUN",
        hh["fix_correct_NOUN"] > hh["base_correct_NOUN"],
        f"base={hh['base_correct_NOUN']}/{hh['n']} -> fix={hh['fix_correct_NOUN']}/{hh['n']}")

    # ---- W4 DOWNSTREAM CASCADE -------------------------------------------------------------------
    dr = P.downstream_recovery()
    case1 = next(c for c in dr["cases"] if "medic" == c["head"])
    chk("W4a downstream: 'blocked the medic from saving' recovers HELP->HARM (POS fix -> parse binds "
        "patient + attaches from-clause -> composed harm/help types PREVENT-a-good = HARM)",
        case1["harm_help_before"] != "HARM" and case1["harm_help_after"] == "HARM"
        and case1["head_dep_after"] == "dobj",
        f"before={case1['harm_help_before']} after={case1['harm_help_after']} dep={case1['head_dep_after']}")

    st = P.downstream_live_stacked()
    chk("W4b downstream (live reader): 'bullied the intern' recovers HARM ONLY with BOTH fixes "
        "(POS binds 'intern' as patient; arithmetic types 'bully'=HARM) -- neither alone",
        st["recovered_only_with_both"],
        f"stock={st['stock']} pos_only={st['pos_fix_only']} both={st['both_fixes']}")

    npass = sum(1 for c in results if c)
    print(f"\n{npass}/{len(results)} PASS")
    return npass == len(results)


if __name__ == "__main__":
    raise SystemExit(0 if test_pos_nominal_head_correction() else 1)
