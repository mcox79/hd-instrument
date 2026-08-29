"""Scaffold-free witness for the situation-model TIME dimension (temporal-order register).
Reproduces the load-bearing claims of notes/problems/situation_model_has_no_tested_temporal_order_comprehension.
Writes nothing; asserts the headlines. Run: .venv/Scripts/python.exe verification/test_temporal_order_register.py
"""
from __future__ import annotations

import os
import sys
import warnings

warnings.filterwarnings("ignore")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import _temporal_order_register as R
from experiments import exp_temporal_order_distance_effect_v1 as DE

PASS = []


def check(name, cond):
    PASS.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    assert cond, name


def sents(text):
    return [text.split()]


print("== 1. before(x,y) on the four discriminating structures ==")
# past-perfect flashback: narration WRONG, register RIGHT
ev, tg, ed = R.extract_passage(sents("He arrived . She had already left ."), clause_pluperfect=True)
narr = R.NarrationOrderFloor(ev, tg, ed)
comp = R.ComposedRegister(R.DiscreteOrderRegister(ev, tg, ed), narr)
check("pp-flashback narration is WRONG (left after arrived)", narr.before("left", "arrived").pred == R.AFTER)
check("pp-flashback register is RIGHT (left before arrived)", comp.before("left", "arrived").pred == R.BEFORE)
# connective-only reorder (NO 'had' -> the live reader's had-gate DROPS this)
ev, tg, ed = R.extract_passage(sents("Before he ate , he prayed ."), clause_pluperfect=True)
d2 = R.DiscreteOrderRegister(ev, tg, ed)
check("connective-only reorder RIGHT (prayed before ate)", d2.before("prayed", "ate").pred == R.BEFORE)
# linear control: register must not confidently invert (abstain -> narration = right)
ev, tg, ed = R.extract_passage(sents("He opened the door and walked inside ."), clause_pluperfect=True)
c3 = R.ComposedRegister(R.DiscreteOrderRegister(ev, tg, ed), R.NarrationOrderFloor(ev, tg, ed))
check("linear control not inverted (opened before walked)", c3.before("opened", "walked").pred == R.BEFORE)

print("== 2. brain-faithful clause-pluperfect fix: had...stood no longer confidently WRONG ==")
ev, tg, ed = R.extract_passage(
    sents("precisely such had the paragraph originally stood from the printer s hands "
          "but sir walter had improved it"), clause_pluperfect=True)
disc = R.DiscreteOrderRegister(ev, tg, ed)
check("stood/improved not confidently inverted (abstain or correct)",
      disc.before("stood", "improved").pred != R.AFTER)

print("== 3. info-free twin (edge-direction scrambled) collapses toward chance ==")
ev, tg, ed = R.extract_passage(sents("He arrived . She had already left ."), clause_pluperfect=True)
import random
flips = 0
for s in range(200):
    te = R.make_twin_edges(ed, random.Random(s))
    tw = R.ComposedRegister(R.DiscreteOrderRegister(ev, tg, te), R.NarrationOrderFloor(ev, tg, ed))
    flips += int(tw.before("left", "arrived").pred == R.BEFORE)
check("twin ~chance on the flashback pair (not always right)", 0.2 < flips / 200 < 0.8)

print("== 4. representation fork: continuous margin shows the distance effect; discrete flat ==")
disc_d, cont_d, _, _, _, _, _ = DE.eval_condition(7, 40, 0.0, DE.SEED, d=256)
slope = DE._slope(cont_d, "mean_margin")
dslope = DE._slope(disc_d, "acc")
check("continuous margin increases with temporal distance (slope > 0)", slope is not None and slope > 0.05)
check("discrete accuracy is flat with distance (|slope| ~ 0)", abs(dslope) < 1e-6)

print(f"\n{sum(1 for _, ok in PASS if ok)}/{len(PASS)} checks PASS")
