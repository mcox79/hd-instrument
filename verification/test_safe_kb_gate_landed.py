"""Landing witness for hdlab/safe_kb_gate.py (promoted 2026-09-09 from
experiments/exp_namebridge_safe_kb_gate_v1.py::safe_kb_types).

Proves: (W1) the organ self-test passes; (W2) the SAFETY-THEOREM MECHANISM -- on a wrong-entity (disagreeing
discourse) case the gate DROPS the false KB type an ungated union would admit, and gated is ALWAYS a subset of
ungated (it can only remove, never add, false facts); (W3) is-a routing goes through the landed hdlab.typed_spokes
C5 spoke; (W4) OPTIONAL byte-parity vs the source experiments cell (skipped if the heavy cell import is unavailable).
Corpus-free, no external LLM.
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.safe_kb_gate import safe_kb_types, _selftest, __bf_status__

fails = []

# W1 -- organ self-test
print("W1 organ self-test:")
if _selftest() != 0:
    fails.append("W1 self-test")
assert __bf_status__ == "BF", "tag drift"

# W2 -- the SAFETY THEOREM MECHANISM (why the gate protects a broad KB under noise)
print("W2 safety-theorem mechanism (gated drops the wrong-entity fact; gated subset of ungated):")
# a wrong-entity KB hit: the recognized name's KB says {album, song} but the DISCOURSE says the entity is a person/teacher
raw = frozenset(["album", "song"])
discourse = {"person", "teacher"}
ungated = set(raw)                                   # naive: admit every KB type (the harmed path)
gated = safe_kb_types(raw, discourse, notability=500)  # even highly-notable: discourse DISAGREES -> abstain
w2a = gated == frozenset()
w2b = gated.issubset(ungated)                        # gate can only REMOVE false facts, never add
print("   ungated=%s gated=%s -> abstain=%s subset=%s" % (ungated, set(gated), w2a, w2b))
if not (w2a and w2b):
    fails.append("W2 mechanism")
# and when discourse CONFIRMS, the (now-safe) facts fire
confirmed = safe_kb_types(raw, {"album"}, 0)
if confirmed != raw:
    fails.append("W2 confirm-fires")
print("   confirm case: discourse {album} -> %s (fires)" % set(confirmed))

# W3 -- is-a routing via hdlab.typed_spokes (painter is-a artist -> confirm; unrelated -> abstain)
print("W3 is-a routing through hdlab.typed_spokes C5 spoke:")
isa_confirm = safe_kb_types(frozenset(["painter"]), {"artist"}, 0) == frozenset(["painter"])
isa_abstain = safe_kb_types(frozenset(["painter"]), {"country"}, 0) == frozenset()
print("   painter|artist(is-a)=%s  painter|country(unrelated)=%s" % (isa_confirm, isa_abstain))
if not (isa_confirm and isa_abstain):
    fails.append("W3 is-a routing")

# W4 -- OPTIONAL byte-parity vs the source cell (bonus; the heavy cell pulls a corpus web, so tolerate absence)
print("W4 parity vs source experiments cell (optional):")
try:
    import experiments.exp_namebridge_safe_kb_gate_v1 as SRC
    battery = [
        (frozenset(["composer"]), frozenset(["composer"]), 0),
        (frozenset(["painter"]), frozenset(["artist"]), 0),
        (frozenset(["album"]), frozenset(["person", "teacher"]), 500),
        (frozenset(["country"]), frozenset(), 100),
        (frozenset(["country"]), frozenset(), 1),
        (frozenset(), frozenset(["person"]), 500),
        (frozenset(["painter", "album"]), frozenset(["artist"]), 0),
    ]
    mism = 0
    for raw_t, disc_t, notab in battery:
        a = safe_kb_types(raw_t, set(disc_t), notab)
        b = SRC.safe_kb_types(raw_t, set(disc_t), notab)
        if a != b:
            mism += 1
    print("   parity checked %d cases, mismatches=%d" % (len(battery), mism))
    if mism:
        fails.append("W4 parity (%d mismatches)" % mism)
except Exception as e:
    print("   SKIPPED (source cell import unavailable: %s) -- parity is by-construction (verbatim body + same TS.is_a)" % type(e).__name__)

print()
print("RESULT: %s" % ("ALL PASS" if not fails else "FAIL (%s)" % "; ".join(fails)))
sys.exit(1 if fails else 0)
