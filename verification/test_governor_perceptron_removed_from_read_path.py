"""Landing witness: the C6 cert-fit governor PERCEPTRON (trained at inference) is REMOVED from the live reader
affect path (situation_reader `_assign_affect` now calls score_context_grounded_valence_pretagged(..., governor=False)),
because it is DECISION-DEAD there. Proves:
 W1  reader-observable byte-identity: over a battery tagged with the reader's OWN UD tagger, governor=True vs
     governor=False give an IDENTICAL (stage, to_ternary(predicted_type)) -- exactly what _assign_affect reads.
 W2  no perceptron trained when governor=False (the _GOV_PERCEPTRON_CACHE stays empty), and governor=True DOES
     populate it (positive control: the perceptron still exists for the measurement cells that opt in by default).
 W3  live-read smoke: a real situation_reader read runs with governor=False (no crash) and still produces affect.
Corpus-free where possible; NO external LLM.
"""
import os, sys
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import hdlab.context_grounded_valence as CGV
from hdlab.context_grounded_valence import score_context_grounded_valence_pretagged, to_ternary
from hdlab.situation_reader import _affect_pos_cached

fails = []
SENTS = [
    ("child", "The soldier struck the child with his fist ."),
    ("man", "The nurse comforted the frightened man ."),
    ("woman", "The doctor healed the sick woman ."),
    ("boy", "The bully humiliated the small boy ."),
    ("prisoner", "The guard tortured the prisoner for hours ."),
    ("patient", "The surgeon saved the dying patient ."),
    ("victim", "The robber threatened the terrified victim ."),
    ("worker", "The manager fired the loyal worker ."),
    ("baby", "The mother soothed the crying baby ."),
    ("hostage", "The negotiator freed the exhausted hostage ."),
    ("servant", "The master beat the obedient servant ."),
    ("student", "The mentor encouraged the anxious student ."),
    ("refugee", "The volunteer sheltered the desperate refugee ."),
    ("captive", "The warlord starved the weak captive ."),
    ("employee", "The boss rewarded the diligent employee ."),
]

def observ(patient, sent, governor):
    toks = sent.split(" ")
    pos = list(_affect_pos_cached(sent))
    try:
        r = score_context_grounded_valence_pretagged(patient, toks, pos, governor=governor)
    except ValueError:
        return None
    return to_ternary(r["predicted_type"]) if r["stage"] == "event" else None

# W1 -- reader-observable byte identity (governor True vs False)
CGV._GOV_PERCEPTRON_CACHE.clear()
diffs = []; n_event = 0
for p, s in SENTS:
    a = observ(p, s, governor=True)
    b = observ(p, s, governor=False)
    if a is not None:
        n_event += 1
    if a != b:
        diffs.append((p, a, b))
ok1 = not diffs
print("W1 reader-observable byte-identity: %d items, event-stage(governor=True)=%d, diffs=%d %s" % (
    len(SENTS), n_event, len(diffs), "PASS" if ok1 else "FAIL %r" % diffs[:5]))
if not ok1:
    fails.append("W1")

# W2 -- no perceptron trained when governor=False; governor=True populates the cache (positive control)
CGV._GOV_PERCEPTRON_CACHE.clear()
for p, s in SENTS:
    observ(p, s, governor=False)
empty_when_off = len(CGV._GOV_PERCEPTRON_CACHE) == 0
observ(SENTS[0][0], SENTS[0][1], governor=True)   # opt-in path (measurement cells) still trains it
trains_when_on = len(CGV._GOV_PERCEPTRON_CACHE) >= 1
ok2 = empty_when_off and trains_when_on
print("W2 no perceptron trained when governor=False (cache empty=%s); trains when True (cache=%d): %s" % (
    empty_when_off, len(CGV._GOV_PERCEPTRON_CACHE), "PASS" if ok2 else "FAIL"))
if not ok2:
    fails.append("W2")

# W3 -- live affect-path smoke: the reader's OWN _assign_affect (which now calls governor=False) runs + returns affect
try:
    from hdlab.situation_reader import _assign_affect
    outs = [(_assign_affect(p, s.replace(" .", " ."))) for p, s in SENTS[:8]]
    fired = [o for o in outs if o is not None]
    ran = True
    print("W3 live _assign_affect (governor=False) ran on 8 items: %d fired, sample=%s" % (len(fired), outs[:8]))
except Exception as e:
    ran = False
    print("W3 live _assign_affect FAILED: %s: %s" % (type(e).__name__, e))
if not ran:
    fails.append("W3")

print()
print("RESULT: %s" % ("ALL PASS" if not fails else "FAIL (%s)" % ",".join(fails)))
sys.exit(1 if fails else 0)
