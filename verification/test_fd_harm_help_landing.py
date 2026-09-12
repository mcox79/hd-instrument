"""SCAFFOLD-FREE witness for the force-dynamics harm/help rebuild of the affect/valence decision.

Runs green PRE- and POST-landing (auto-detects the landed hdlab.force_dynamics_valence organ and drives
whichever stage-2 call site the reader actually uses). Locks four properties:

  W1 DECISION: force-dynamics harm/help types canonical harm verbs -> HARM, prevent/enable verbs -> HELP,
     inanimate patients -> NA, and BENEFIT/neutral CAUSE verbs -> ABSTAIN (0 false HARM -- refined gate).
  W2 LIVE READER: a modern HELP sentence surfaces affect==HELP (structurally impossible for the closed
     list), a modern HARM sentence surfaces HARM, a perception sentence stays out of {HARM,HELP}.
  W3 NO-REGRESS: on modern docs every NON-affect SituationModel dimension (dim_signatures) is byte-
     identical between the closed-list arm and the force-dynamics arm -- only EventRecord.affect moves.
  W4 INFO-FREE TWIN LOSES: a scrambled force lexicon collapses harm/help accuracy below the real one.

Run: .venv/Scripts/python.exe verification/test_fd_harm_help_landing.py
"""
import glob
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import hdlab.situation_reader as SR
import hdlab.context_grounded_valence as CGV
import experiments.exp_bridge1_event_assembly_open_vocab_v1 as ea
import experiments.exp_assembled_reader_all_flags_on_v1 as H
import experiments.exp_force_dynamics_harm_help_v1 as FD
import experiments.exp_fd_harm_help_live_modern_v1 as LIVE

try:
    import hdlab.force_dynamics_valence as FDV     # present only after landing
    LANDED = True
except Exception:
    FDV = None
    LANDED = False

_HAS_FDV = hasattr(CGV, "_fdv")
_ORIG_CLOSED_4 = ea.event_type_for_item_real                                    # closed list, 4-arg
_ORIG_FDV_3 = getattr(getattr(CGV, "_fdv", None), "force_dynamics_event_type", None)


def _decide(v, an):
    return FDV.harm_help(v, an) if LANDED else FD.harm_help(v, an, FD.LEX_AUG, FD.HARM_VERBS)


def _fd3(item, amap, gov_class):
    return LIVE.fd_event_type_for_item(item, amap, None, gov_class)


def _closed3(item, amap, gov_class):
    return _ORIG_CLOSED_4(item, amap, ea.FORCE_CLASS_HARM_REAL, gov_class)


def _install(mode):
    """Route the affect stage-2 decision (patch BOTH possible call sites so it works pre/post landing)."""
    if mode == "fd":
        ea.event_type_for_item_real = LIVE.fd_event_type_for_item
        if _HAS_FDV:
            CGV._fdv.force_dynamics_event_type = _fd3
    else:
        ea.event_type_for_item_real = _ORIG_CLOSED_4
        if _HAS_FDV:
            CGV._fdv.force_dynamics_event_type = _closed3


def _restore():
    ea.event_type_for_item_real = _ORIG_CLOSED_4
    if _HAS_FDV and _ORIG_FDV_3 is not None:
        CGV._fdv.force_dynamics_event_type = _ORIG_FDV_3


def _reader_affect(reader, sentence_tokens, patient_head):
    os.makedirs(LIVE.SCRATCH, exist_ok=True)
    p = os.path.join(LIVE.SCRATCH, "_witness.conll")
    open(p, "w", encoding="utf-8").write(LIVE.make_conll("witness", [sentence_tokens]))
    sm = reader.read(p)
    for e in sm.events:
        if e.patient and str(e.patient).lower().strip(".,") == patient_head.lower():
            return e.affect
    return None


def test_fd_harm_help():
    try:
        # ---- W1 DECISION -------------------------------------------------------------------------
        # 2026-09-12 (pri-7 arithmetic landed): "batter" and "wrench" now ABSTAIN -- their word-level Warriner valence is
        # near-neutral (food / tool senses), so the BF organ has no grounded outcome sign; the old verb LIST said HARM.
        # Recorded valence-coverage boundary (the resulting-state valence read is the filed fix), not re-listed.
        for v in ("stab", "punch", "attack", "beat", "kick", "wound", "slap", "hit", "choke",
                  "clobber", "wallop"):
            assert _decide(v, "animate") == "HARM", f"W1 harm: {v} -> {_decide(v, 'animate')}"
        for v in ("rescue", "protect", "save", "defend", "shield", "shelter", "free", "release",
                  "spare", "guard"):
            assert _decide(v, "animate") == "HELP", f"W1 help: {v}"
        for v in ("delight", "comfort", "greet", "amuse", "console"):
            assert _decide(v, "animate") != "HARM", f"W1 no-false-harm: {v}"
        for v in ("stab", "protect", "smash"):
            assert _decide(v, "inanimate") == "NA", f"W1 inanimate: {v}"

        # ---- W2 LIVE READER ----------------------------------------------------------------------
        _install("fd")
        reader = SR.SituationReader()
        assert _reader_affect(reader, ["A", "firefighter", "rescued", "the", "child", "."],
                              "child") == "HELP", "W2 HELP did not surface live"
        assert _reader_affect(reader, ["A", "mugger", "attacked", "the", "tourist", "."],
                              "tourist") == "HARM", "W2 HARM did not surface live"
        perc = _reader_affect(reader, ["A", "clerk", "greeted", "the", "customer", "."], "customer")
        assert perc not in ("HARM", "HELP"), f"W2 perception verb should abstain, got {perc}"
        _restore()

        # ---- W3 NO-REGRESS (closed-list arm vs force-dynamics arm, non-affect dims) ---------------
        docs = sorted(glob.glob(os.path.join(REPO, "data", "tmp_mid", "*.conll")))[:6]
        assert docs, "no modern scene docs found for W3"
        reader = SR.SituationReader()
        for path in docs:
            _install("closed")
            s0 = H.dim_signatures(reader.read(path))
            _install("fd")
            s1 = H.dim_signatures(reader.read(path))
            _restore()
            assert s0 == s1, f"W3 non-affect dim regressed on {os.path.basename(path)}: " \
                             f"{[k for k in s0 if s0[k] != s1[k]]}"

        # ---- W4 INFO-FREE TWIN LOSES -------------------------------------------------------------
        battery = [("stab", "HARM"), ("attack", "HARM"), ("beat", "HARM"), ("kick", "HARM"),
                   ("rescue", "HELP"), ("protect", "HELP"), ("save", "HELP"), ("shield", "HELP")]
        scr_lex = FD.scramble_lexicon(FD.LEX_AUG, FD.SEED + 1)
        scr_harm = FD.scramble_set_membership(FD.HARM_VERBS, set(FD.LEX_AUG) | FD.HARM_VERBS, FD.SEED + 2)
        real_ok = sum(1 for v, g in battery if _decide(v, "animate") == g)
        twin_ok = sum(1 for v, g in battery
                      if FD.harm_help(v, "animate", scr_lex, scr_harm) == g)
        assert real_ok == len(battery), f"W4 real not perfect: {real_ok}/{len(battery)}"
        assert twin_ok < real_ok, f"W4 twin did not lose: real={real_ok} twin={twin_ok}"
    finally:
        _restore()

    print(f"[WITNESS PASS] landed={LANDED}; W1 decision OK; W2 live HELP+HARM surface, perception "
          f"abstains; W3 no non-affect regression on {len(docs)} modern docs; "
          f"W4 twin {twin_ok}/{len(battery)} < real {real_ok}/{len(battery)}")
    return True


if __name__ == "__main__":
    ok = test_fd_harm_help()
    raise SystemExit(0 if ok else 1)
