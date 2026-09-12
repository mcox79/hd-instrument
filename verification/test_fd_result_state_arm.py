"""Witness for the RESULT-STATE ARM of hdlab/force_dynamics_valence.py (strategy 2026-09-12, pri-14 research landing).

The harm/help endstate valence is read FIRST from the RESULT STATE the patient is left in (VerbNet class semantics
keyed by WordNet sense; offline asset data/frontend_assets/verbnet_result_state_v1.json), then from the verb's
word-level norm. Locks:

  W1 RECOVERY: the assault verbs the word-level norm abstained on or mis-signed (batter, bludgeon, pummel, club,
     throttle, clobber, wallop, thrash, whack) -> HARM for an animate patient; wrench / maul (no animate-contact
     sense with a result state in the foundation, weak norm) ABSTAIN -- the recorded honest boundary.
  W2 POPULATIONS HOLD (the solver's exp_fd_harm_help_arithmetic_v1 sets): harm-frame 10/10 HARM; social-harm and
     non-prevent help no lower than the word-level-only read (oppress, tend, and one gate-held verb each abstain as
     before); NO neutral verb reads HARM or HELP; no wrong-sign decision anywhere.
  W3 CONSISTENCY, NOT A SECOND OPINION: where both the result-state value and the word-level sign exist over the
     affecting Warriner verbs, they agree >= 0.80 (n >= 50); every disagreement is a result-state HARM read on a
     verb whose norm is positive through another sense (club / brain / birch / throttle ...).
  W4 INFO-FREE TWIN LOSES: scrambling the sense-key -> class assignment of the asset collapses the recovery set.
  W5 NO LIST: the asset is keyed by WordNet sense keys derived from VerbNet MEMBER entries; it names >= 200 sense
     keys and the arm abstains gracefully (falls back to the norm) when the asset is absent.
  W6 LIVE BOARD GOLD: every HARM/HELP item of exp_fd_harm_help_live_modern_v1.GOLD keeps its verdict via harm_help.

Run: .venv/Scripts/python.exe verification/test_fd_result_state_arm.py
"""
import os
import random
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import hdlab.force_dynamics_valence as FDV
import experiments.exp_fd_harm_help_arithmetic_v1 as A
import experiments.exp_fd_harm_help_live_modern_v1 as LIVE

RECOVERY = ["batter", "bludgeon", "pummel", "club", "throttle", "clobber", "wallop", "thrash", "whack"]
STATE_DECIDED = ["batter", "bludgeon", "pummel", "club", "throttle"]   # decided by the result state (norm absent/weak/wrong-sense)
# (stomp is held back by the pre-existing graded AFFECTEDNESS gate, not by this arm -- out of scope here)
BOUNDARY = ["wrench", "maul"]
fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        fails.append(name)


# W1
got = {v: FDV.harm_help(v, "animate") for v in RECOVERY}
check("W1 recovery -> HARM", all(g == "HARM" for g in got.values()), str(got))
bnd = {v: FDV.harm_help(v, "animate") for v in BOUNDARY}
check("W1 boundary abstains (wrench, maul)", all(g is None for g in bnd.values()), str(bnd))

# W2
def _counts():
    FDV._EV_CACHE.clear()
    return (sum(FDV.harm_help(v, "animate") == "HARM" for v in A.P_HARM_FRAME),
            sum(FDV.harm_help(v, "animate") == "HARM" for v in A.P_SOCIAL_HARM),
            sum(FDV.harm_help(v, "animate") == "HELP" for v in A.P_NONPREVENT_HELP))
hf, sh, hp = _counts()
FDV.RESULT_STATE_READ = False
hf0, sh0, hp0 = _counts()                                   # the word-level-only read (the organ before this arm)
FDV.RESULT_STATE_READ = True
FDV._EV_CACHE.clear()
neu = [(v, FDV.harm_help(v, "animate")) for v in A.P_NEUTRAL_BROAD if FDV.harm_help(v, "animate") in ("HARM", "HELP")]
wrong = [(v, FDV.harm_help(v, "animate")) for v in A.P_HARM_FRAME + A.P_SOCIAL_HARM if FDV.harm_help(v, "animate") == "HELP"]
wrong += [(v, FDV.harm_help(v, "animate")) for v in A.P_NONPREVENT_HELP if FDV.harm_help(v, "animate") == "HARM"]
check("W2 harm-frame 10/10", hf == len(A.P_HARM_FRAME), f"{hf}/{len(A.P_HARM_FRAME)}")
check("W2 social-harm no-regress vs word-only", sh >= sh0 and sh >= 14, f"{sh}/{len(A.P_SOCIAL_HARM)} (word-only {sh0})")
check("W2 non-prevent help no-regress vs word-only", hp >= hp0 and hp >= 14, f"{hp}/{len(A.P_NONPREVENT_HELP)} (word-only {hp0})")
check("W2 no wrong-sign decision", not wrong, str(wrong))
check("W2 neutral precision held", not neu, str(neu))

# W3
try:
    from nltk.corpus import wordnet as wn
    afx = FDV._afx()
    verbs = [w for w in afx.val if " " not in w and wn.synsets(w, "v") and FDV.is_affecting(w)]
except Exception as e:  # pragma: no cover
    verbs = []
    check("W3 vocabulary available", False, repr(e))
both = []
for v in verbs:
    sv = FDV.result_state_value(v)
    wv = afx.valence(FDV.lemmatize_verb(v))
    if sv is not None and abs(sv) >= FDV.STATE_MIN and wv is not None and abs(wv) >= FDV.WEAK_VALENCE:
        both.append((v, 1 if sv > 0 else -1, 1 if wv > 0 else -1))
agree = sum(1 for _, a, b in both if a == b)
disagree = [(v, a, b) for v, a, b in both if a != b]
check("W3 agreement with the word-level sign >= 0.80 (n >= 50)", len(both) >= 50 and agree / max(1, len(both)) >= 0.80,
      f"{agree}/{len(both)} = {agree / max(1, len(both)):.2f}")
check("W3 every disagreement is a state-HARM over a positive norm", all(a == -1 and b == 1 for _, a, b in disagree),
      str([v for v, _, _ in disagree]))
n_decided = sum(1 for v in verbs if FDV.endstate_valence_sign(v) is not None)
n_state = sum(1 for v in verbs if FDV.result_state_value(v) is not None)
print(f"     coverage: {len(verbs)} affecting verbs; {n_state} carry a result state; {n_decided} decided overall")

# W4 twin: the asset's state entries re-assigned to RANDOM WordNet verb sense keys (the whole universe, not only the
# 233 keys that carry a state) -- the same information content, no alignment between sense and result state.
table = FDV.result_state_table()
universe = sorted({lm.key().split("::")[0] for ss in wn.all_synsets("v") for lm in ss.lemmas()})
rng = random.Random(0)
twin = dict(zip(rng.sample(universe, len(table)), [table[k] for k in sorted(table)]))
twin_hits = sum(FDV.harm_help_arithmetic(v, "animate", states=twin) == "HARM" for v in STATE_DECIDED)
real_hits = sum(FDV.harm_help_arithmetic(v, "animate") == "HARM" for v in STATE_DECIDED)
check("W4 twin loses on the state-decided verbs", twin_hits < real_hits and real_hits == len(STATE_DECIDED),
      f"twin {twin_hits}/{len(STATE_DECIDED)} vs real {real_hits}/{len(STATE_DECIDED)}")
keys = sorted(table)

# W5
check("W5 asset names >= 200 sense keys", len(table) >= 200, f"{len(table)} keys")
check("W5 asset keyed by WordNet sense keys", all("%2:" in k for k in keys), "")
_saved = FDV._RS_TABLE
try:
    FDV._RS_TABLE = {}
    FDV._RS_CACHE.clear()
    FDV._EV_CACHE.clear()
    fb = FDV.endstate_valence_sign("stab")          # strong negative norm -> still decided by the norm
    ab = FDV.endstate_valence_sign("batter")        # weak norm, no asset -> abstains (no list behind it)
    check("W5 absent asset -> word-level fallback, no hidden list", fb == -1 and ab is None, f"stab={fb} batter={ab}")
finally:
    FDV._RS_TABLE = _saved
    FDV._RS_CACHE.clear()
    FDV._EV_CACHE.clear()

# W6
bad = []
for g in LIVE.GOLD:
    agent, verb, patient, label = g[0], g[1], g[2], g[3]
    if label in ("HARM", "HELP"):
        got = FDV.harm_help(verb, "animate")
        if got != label:
            bad.append((verb, got, label))
check("W6 live board gold HARM/HELP verdicts hold", not bad, str(bad))

print("\nRESULT:", "ALL GREEN" if not fails else f"FAILED {fails}")
sys.exit(1 if fails else 0)
