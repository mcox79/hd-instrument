"""Witness for the TESTIMONY route with reliability (from the sequential-registration drill; Harris & Koenig
2006 testimony as an independent channel; Koenig, Clement & Harris 2004 informant-reliability discounting).

The single-move RULE 2 only handled HONEST testimony (told -> knows reality). This makes testimony a first-class
event that writes the ASSERTED location to the per-agent ledger:
  1. TOLD THE TRUTH  -> true belief (asserted == reality).
  2. BELIEVED A LIE  -> FALSE belief MATCHING the lie (asserted != reality) -- the single-move gate cannot express
     "believes X where X is neither the initial nor the true location".
  3. DISTRUSTED SOURCE -> DISCOUNTED: the addressee keeps its PRIOR belief (Koenig reliability). Cases 2 and 3
     assert the SAME location; only trust differs -> different belief. That is the discriminator.

Run: .venv/Scripts/python.exe verification/test_testimony_reliability.py   -- writes to NO landed dir.
"""
from __future__ import annotations
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import spacy
from experiments.perceptual_access_ledger import PerceptualAccessLedger

AL = lambda name: [name, "he", "she", "they", "him", "her", "them", "his"]
BASE = ("Anna put the marble in the red box. Anna went to the market. "
        "While Anna was away, Ben moved the marble from the red box to the blue drawer. ")
MOVES = [{"obj": "marble", "to": "red box", "event_index": 0, "mover": "Anna"},
         {"obj": "marble", "to": "blue drawer", "event_index": 2, "mover": "Ben"}]


def main():
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)

    # ---- 1. told the truth -> true belief ----
    t1 = BASE + "When Anna returned, Ben told her the marble was now in the blue drawer."
    ch1 = MOVES + [{"type": "tell", "obj": "marble", "asserted": "blue drawer", "addressee": "Anna", "event_index": 3}]
    reg, world = led.sequential_registration(t1, {"Anna": AL("Anna")}, ch1)
    b = led.belief_of(reg, "Anna", "marble")
    assert b == "blue drawer" and not led.is_false_belief(reg, world, "Anna", "marble"), \
        f"[1] told-the-truth: Anna should TRUE-believe 'blue drawer', got {b!r}"
    print(f"[1] PASS  told-the-truth: Anna believes {b!r} (reality={world['marble']!r}) -- TRUE belief via testimony")

    # ---- 2. believed a lie -> false belief matching the lie ----
    t2 = BASE + "When Anna returned, Ben lied and told her the marble was in the green chest."
    ch2 = MOVES + [{"type": "tell", "obj": "marble", "asserted": "green chest", "addressee": "Anna", "event_index": 3}]
    reg, world = led.sequential_registration(t2, {"Anna": AL("Anna")}, ch2)
    b = led.belief_of(reg, "Anna", "marble")
    assert b == "green chest", f"[2] believed-a-lie: Anna should believe the LIE 'green chest', got {b!r}"
    assert led.is_false_belief(reg, world, "Anna", "marble"), "[2] and it is FALSE (reality=blue drawer)"
    print(f"[2] PASS  believed-a-lie: Anna believes {b!r} (reality={world['marble']!r}) -- FALSE belief matching the lie")

    # ---- 3. distrusted source -> discounted, keeps prior belief ----
    t3 = BASE + "When Anna returned, Ben told her it was in the green chest, but Anna did not believe him."
    ch3 = MOVES + [{"type": "tell", "obj": "marble", "asserted": "green chest", "addressee": "Anna", "event_index": 3}]
    reg, world = led.sequential_registration(t3, {"Anna": AL("Anna")}, ch3)
    b = led.belief_of(reg, "Anna", "marble")
    assert b == "red box", f"[3] distrusted-source: Anna should KEEP her prior 'red box', not adopt the claim, got {b!r}"
    print(f"[3] PASS  distrusted-source: Anna believes {b!r} (reality={world['marble']!r}) -- DISCOUNTED the untrusted claim (Koenig)")

    print("\nALL 3 TESTIMONY-RELIABILITY ASSERTIONS PASSED -- testimony writes the ASSERTED location to the ledger: "
          "honest telling gives a true belief, a believed lie gives a false belief matching the lie, and a "
          "distrusted source is discounted (the addressee keeps its prior belief). Cases 2 and 3 assert the SAME "
          "location and diverge only on trust.")


if __name__ == "__main__":
    main()
