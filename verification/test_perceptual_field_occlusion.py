"""Discriminating witness for the PER-MODALITY perceptual field (occlusion) gate.

From the occlusion / Level-1-VPT research drill: a faithful field gate must make distinctions a COARSE keyword
gate (dark/asleep/barrier treated as one uniform blocker, no opacity, no loudness) CANNOT:
  1. TRANSPARENT vs CLOSED-OPAQUE container -- same scene, opacity flips observed (the Ullman transparent-bag case).
  2. SILENT vs LOUD change in the DARK -- darkness blocks VISION only; a noisy move is still HEARD.
  3. Co-present BEHIND A SCREEN -- opaque barrier blocks vision though the agent is in the room and awake.
  4. Present but NOT ATTENDING (absorbed in a book) -- vision needs attention, not just presence + light.

Asserts the ledger gets ALL FOUR right, and that a coarse single-gate baseline FAILS the two it structurally
cannot make (opacity flip, loudness-in-dark). RULE 0 is OFF (no epistemic markers) so the FIELD gate decides.

Run: .venv/Scripts/python.exe verification/test_perceptual_field_occlusion.py   -- writes to NO landed dir.
"""
from __future__ import annotations
import os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import spacy
from experiments.perceptual_access_ledger import PerceptualAccessLedger

# (name, text, event_index, expected_observed, note)
CASES = [
    ("transparent_container",
     "The lamp was lit and Anna stood beside the little table. Ben slipped the ring into a glass case on the table.",
     1, True, "glass (transparent) -> vision sees the move"),
    ("closed_opaque_container",
     "The lamp was lit and Anna stood beside the little table. Ben slipped the ring into a closed iron box on the table.",
     1, False, "closed opaque box -> vision blocked, quiet -> not heard"),
    ("dark_silent",
     "The candle was out and Anna sat in the darkness, wide awake. Ben silently carried the marble to the far drawer.",
     1, False, "dark -> no vision; silent -> not heard"),
    ("dark_loud",
     "The candle was out and Anna sat in the darkness, wide awake. Ben stumbled with a loud crash and knocked the marble into the drawer.",
     1, True, "dark -> no vision, BUT the loud crash is HEARD"),
    ("behind_screen",
     "Anna stood in the well-lit room. Ben moved the marble to the box behind a tall screen.",
     1, False, "opaque barrier -> vision blocked despite co-presence"),
    ("not_attending",
     "Anna sat in the lit parlour, absorbed in her book. Ben quietly moved the marble to the box.",
     1, False, "absorbed -> not attending -> vision off; quiet -> not heard"),
]

# COARSE single-gate baseline: present AND not(dark OR asleep OR barrier OR absorbed). No opacity, no loudness.
_COARSE_BLOCK = re.compile(r"\b(dark|darkness|asleep|unconscious|behind a|behind the|absorbed|back turned|blindfold)\b", re.I)
def coarse_gate(text):
    return not _COARSE_BLOCK.search(text)  # observed unless a coarse blocker keyword appears


def main():
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)
    ledger_ok = coarse_fail = 0
    coarse_failed_on = []
    print("case                      expected  ledger  coarse")
    for name, text, ev, exp, note in CASES:
        tr = led.observed(text, ["Anna", "she", "her"], event_index=ev, use_epistemic=False)
        c = coarse_gate(text)
        good = (tr.observed == exp)
        ledger_ok += int(good)
        if c != exp:
            coarse_fail += 1
            coarse_failed_on.append(name)
        print(f"  {name:22s}  {exp!s:5s}     {tr.observed!s:5s}   {c!s:5s}   {'OK' if good else 'LEDGER-FAIL'}  ({note})")
        assert good, f"ledger wrong on {name}: got {tr.observed}, expected {exp} | {tr.reason}"

    # the coarse gate MUST fail the two discriminators it cannot represent (opacity flip, loudness-in-dark)
    assert "closed_opaque_container" in coarse_failed_on, "coarse gate should fail the opacity flip"
    assert "dark_loud" in coarse_failed_on, "coarse gate should fail loudness-in-the-dark"
    print(f"\nLEDGER {ledger_ok}/{len(CASES)} correct; COARSE keyword gate fails {coarse_fail}/{len(CASES)} "
          f"({', '.join(coarse_failed_on)}).")
    print("PASS -- the per-modality field gate makes the opacity + loudness distinctions a keyword gate cannot: "
          "a transparent container is seen where an opaque one is not; a loud change in the dark is heard where a "
          "silent one is not; an opaque screen and inattention block vision despite co-presence.")


if __name__ == "__main__":
    main()
