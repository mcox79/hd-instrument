"""Witness for SEQUENTIAL registration + motion-persistence + ignorance-vs-false-belief (from the sequential-
registration research drill). Extends the single-move observation cue to a CHAIN of changes with partial
observation, on the substrate's own ledger. RULE 0/1/2 per-event logic is reused; only the FOLD is new.

Four discriminating cases the SINGLE-MOVE gate (belief_partition's binary initial/final) cannot express:
  1. A->B->C, sees the FIRST move but not the second  -> believes B (last-registered), not A and not C.
  2. WATCHED-INTO-A-BOX then secretly emptied while occluded -> believes the BOX (destination frozen), NOT
     ignorant and NOT the true (drawer) location -- the motion-persistence exception.
  3. ALREADY-HIDDEN before the agent could perceive it -> IGNORANT (registration = None), NOT "believes initial".
  4. TWO AGENTS, one present for a move and one absent -> DIVERGENT per-agent beliefs over one event stream.

Run: .venv/Scripts/python.exe verification/test_sequential_registration.py   -- writes to NO landed dir.
"""
from __future__ import annotations
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import spacy
from experiments.perceptual_access_ledger import PerceptualAccessLedger

AL = lambda name: [name, "he", "she", "they", "him", "her", "them", "his"]


def main():
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)

    # ---- 1. A->B->C, sees first move only -> believes B ----
    t1 = ("Anna put the marble in the red box. Anna watched Ben move it to the blue basket. "
          "Then Anna went outside to play. While Anna was away, Ben moved the marble from the blue basket "
          "to the green drawer.")
    ch1 = [{"obj": "marble", "to": "red box", "event_index": 0, "mover": "Anna"},
           {"obj": "marble", "to": "blue basket", "event_index": 1, "mover": "Ben"},
           {"obj": "marble", "to": "green drawer", "event_index": 3, "mover": "Ben"}]
    reg, world = led.sequential_registration(t1, {"Anna": AL("Anna")}, ch1)
    b = led.belief_of(reg, "Anna", "marble")
    assert b == "blue basket", f"[1] A->B->C: Anna should believe 'blue basket' (last seen), got {b!r}"
    assert led.is_false_belief(reg, world, "Anna", "marble"), "[1] Anna's belief must be FALSE vs reality (green drawer)"
    print(f"[1] PASS  A->B->C see-first-only: Anna believes {b!r} (reality={world['marble']!r}) -- last-registered, not initial/final")

    # ---- 2. Watched-into-box, secretly emptied while occluded -> believes the box (motion-persistence) ----
    t2 = ("The box stood open on the table. Anna watched Ben drop the ring into the box. Then Ben closed the lid. "
          "Later, while Anna had gone to the door, Ben quietly took the ring from the box and hid it in the drawer.")
    ch2 = [{"obj": "ring", "to": "box", "event_index": 1, "mover": "Ben"},
           {"obj": "ring", "to": "drawer", "event_index": 3, "mover": "Ben"}]
    reg, world = led.sequential_registration(t2, {"Anna": AL("Anna")}, ch2)
    b = led.belief_of(reg, "Anna", "ring")
    assert b == "box", f"[2] motion-persistence: Anna watched it go INTO the box -> should believe 'box', got {b!r}"
    assert not led.is_ignorant(reg, "Anna", "ring"), "[2] Anna is NOT ignorant -- she registered the destination"
    assert led.is_false_belief(reg, world, "Anna", "ring"), "[2] and it is now FALSE (reality=drawer)"
    print(f"[2] PASS  watched-into-box: Anna believes {b!r} (reality={world['ring']!r}) -- destination frozen, NOT ignorant")

    # ---- 3. Already hidden before the agent could perceive it -> IGNORANT (not 'believes initial') ----
    t3 = ("Ben locked the ring inside the closed chest before Anna arrived. Then Anna came into the room. "
          "Anna did not know what the chest held. Ben carried the chest away to the attic.")
    ch3 = [{"obj": "ring", "to": "chest", "event_index": 0, "mover": "Ben"}]
    reg, world = led.sequential_registration(t3, {"Anna": AL("Anna")}, ch3)
    assert led.is_ignorant(reg, "Anna", "ring"), \
        f"[3] already-hidden: Anna never perceived the placement -> IGNORANT, got belief {led.belief_of(reg,'Anna','ring')!r}"
    print(f"[3] PASS  already-hidden-before-arrival: Anna is IGNORANT of the ring (belief=None), not a false 'initial' guess")

    # ---- 4. Two agents, one present one absent -> divergent per-agent beliefs ----
    t4 = ("Kate put the doll in the cradle. Kate went to the market. While Kate was away, Ellen moved the doll "
          "from the cradle to the chest. Ellen watched the whole time.")
    ch4 = [{"obj": "doll", "to": "cradle", "event_index": 0, "mover": "Kate"},
           {"obj": "doll", "to": "chest", "event_index": 2, "mover": "Ellen"}]
    reg, world = led.sequential_registration(t4, {"Kate": AL("Kate"), "Ellen": AL("Ellen")}, ch4)
    bk, be = led.belief_of(reg, "Kate", "doll"), led.belief_of(reg, "Ellen", "doll")
    assert bk == "cradle", f"[4] Kate (absent for the move) should believe 'cradle', got {bk!r}"
    assert be == "chest", f"[4] Ellen (the mover) should believe 'chest', got {be!r}"
    assert led.is_false_belief(reg, world, "Kate", "doll") and not led.is_false_belief(reg, world, "Ellen", "doll"), \
        "[4] Kate FALSE, Ellen TRUE -- beliefs must DIVERGE"
    print(f"[4] PASS  two-agent divergence: Kate believes {bk!r} (FALSE), Ellen believes {be!r} (TRUE); reality={world['doll']!r}")

    print("\nALL 4 SEQUENTIAL-REGISTRATION ASSERTIONS PASSED -- folding the per-event observation cue over a chain "
          "yields a sticky per-agent ledger: last-registered-not-final beliefs, motion-persistence through "
          "occlusion, ignorance distinct from false belief, and divergent multi-agent beliefs over one event stream.")


if __name__ == "__main__":
    main()
