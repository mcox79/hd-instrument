"""Witness for the HYPERNYM-CONSENSUS result-state recovery arm (solver, pri-14 remaining scope).

The landed result-state arm abstains on 826 affecting verbs (no VerbNet result state; weak/absent norm).
This arm recovers the genuine HARM verbs among them by inheriting the patient's outcome valence from the
verb's SUPERORDINATE action (WordNet troponymy), trusted only under cross-sense sign CONSENSUS + strength,
read over the AFFECTING ANIMATE-OBJECT senses -- and an upstream guard so a verb whose affecting-animate
superordinate is affect-laden also PASSES the affectedness gate (savage). Locks (scaffold-free; the
Connotation Frames Effect(o) human gold is the INDEPENDENT check, not consulted at inference):

  W1 RECOVERY: savage, victimize, oppress, maul -> HARM under the extended arm (all landed abstentions).
  W2 MANNER-ENCODED ABSTAIN: brutalize, manhandle, gore do NOT read HELP (harm is in the manner adverb,
     the superordinate is affect-neutral -> honest abstain; the recorded boundary).
  W3 NEUTRAL PRECISION: no P_NEUTRAL_BROAD verb reads HARM/HELP under the extended arm (0 leaks).
  W4 SUBJECT-EXPERIENCER STILL EXCLUDED: admire/envy/love/fear abstain (the object is a stimulus).
  W5 TWIN LOSES: scrambling the Warriner valence collapses the named recovery.
  W6 LANDED WINS UNTOUCHED: stab->HARM, comfort->HELP, watch->abstain.
  W7 INDEPENDENT GOLD: extended arm agrees with Connotation-Frames Effect(o) at >= the landed arm and
     >= 0.90 (both decide non-neutral); the NEW residual decisions carry NO wrong-sign vs the gold.
  W8 BOARD LIVE GOLD: every HARM/HELP item of the 36-item modern gold keeps its verdict.

Run: .venv/Scripts/python.exe verification/test_fd_result_state_hypernym_arm.py
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "3")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "3")
os.environ.setdefault("MKL_NUM_THREADS", "3")
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_fd_result_state_hypernym_v1 as E
import experiments.exp_fd_harm_help_arithmetic_v1 as A
from experiments.fetch_connotation_frames_v1 import load_effect_o
import hdlab.force_dynamics_valence as FDV

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        fails.append(name)


ext = E.harm_help_extended
landed = E.harm_help_landed

# W1
rec = {v: ext(v, "animate") for v in ["savage", "victimize", "oppress", "maul"]}
landed_rec = {v: landed(v, "animate") for v in rec}
check("W1 recovery savage/victimize/oppress/maul -> HARM",
      all(rec[v] == "HARM" for v in rec) and all(landed_rec[v] is None for v in rec),
      f"extended={rec} landed={landed_rec}")

# W2
manner = {v: ext(v, "animate") for v in ["brutalize", "manhandle", "gore"]}
check("W2 manner-encoded abstain (not HELP)", all(g != "HELP" for g in manner.values()), str(manner))

# W3
leaks = [(v, ext(v, "animate")) for v in A.P_NEUTRAL_BROAD if ext(v, "animate") in ("HARM", "HELP")]
check("W3 neutral precision (0 leaks on P_NEUTRAL_BROAD)", not leaks, str(leaks))

# W4
subj = {v: ext(v, "animate") for v in ["admire", "envy", "love", "fear"]}
check("W4 subject-experiencer excluded", all(g is None for g in subj.values()), str(subj))

# W5
scr = E._scrambled_afx()
twin = E._with_extended(
    lambda v, afx=None, states=None: E.extended_endstate_sign(v, scr, states),
    lambda v, lexicon=None, afx=None, tau=None: (
        E._LANDED_ISAFFECTING(v, lexicon, afx, tau) or E.hyper_state_sign(v, scr) is not None))
named = E.NAMED_HARM
twin_h = sum(twin(v, "animate") == "HARM" for v in named)
real_h = sum(ext(v, "animate") == "HARM" for v in named)
check("W5 twin loses on named recovery", twin_h < real_h, f"twin {twin_h} < real {real_h}")

# W6
check("W6 landed wins untouched", ext("stab", "animate") == "HARM" and ext("comfort", "animate") == "HELP"
      and ext("watch", "animate") is None,
      f"stab={ext('stab','animate')} comfort={ext('comfort','animate')} watch={ext('watch','animate')}")

# W7 independent gold
gold = load_effect_o()


def glabel(v):
    e = gold.get(FDV.lemmatize_verb(v))
    if e is None:
        return None
    return "HARM" if e < -0.25 else ("HELP" if e > 0.25 else "NEUTRAL")


lem = E._candidate_verbs()


def agree(fn):
    a = t = 0
    for v in lem:
        g = glabel(v)
        p = fn(v, "animate")
        if g in ("HARM", "HELP") and p in ("HARM", "HELP"):
            t += 1
            a += (g == p)
    return a, t


la, lt = agree(landed)
ea, et = agree(ext)
check("W7 CF agreement: extended >= landed and >= 0.90",
      (ea / max(1, et)) >= (la / max(1, lt)) - 1e-9 and (ea / max(1, et)) >= 0.90,
      f"landed {la}/{lt}={la/max(1,lt):.4f}  extended {ea}/{et}={ea/max(1,et):.4f}")
# no wrong-sign among NEW residual decisions vs the gold
residual = [v for v in lem if landed(v, "animate") is None]
wrong = []
for v in residual:
    p = ext(v, "animate")
    g = glabel(v)
    if p in ("HARM", "HELP") and g in ("HARM", "HELP") and p != g:
        wrong.append((v, p, g))
check("W7 no wrong-sign in new residual decisions vs CF", not wrong, str(wrong))

# W8 board live gold
try:
    import experiments.exp_fd_harm_help_live_modern_v1 as LIVE
    bad = [(g[1], ext(g[1], "animate"), g[3]) for g in LIVE.GOLD
           if g[3] in ("HARM", "HELP") and ext(g[1], "animate") != g[3]]
    check("W8 board live gold holds", not bad, str(bad))
except Exception as e:  # pragma: no cover
    check("W8 board live gold available", False, repr(e))

print("\nRESULT:", "ALL GREEN" if not fails else f"FAILED {fails}")
if __name__ == "__main__":
    sys.exit(1 if fails else 0)


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
