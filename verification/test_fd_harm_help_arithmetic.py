"""SCAFFOLD-FREE witness for the FORCE-DYNAMIC ARITHMETIC harm/help rebuild
(experiments/exp_fd_harm_help_arithmetic_v1.py + _live_v1.py). Locks six properties on the current
bytes; runs green PRE-landing (drives the proposed decision by monkeypatching the LIVE decision point
hdlab.force_dynamics_valence.harm_help -- the exact edit the hdlab fix would land).

  W1 DECISION: force-structure x grounded-valence types canonical harm-frame verbs -> HARM, prevent/
     enable -> HELP, SOCIAL/EMOTIONAL harm (mug/evict/bully/humiliate) -> HARM and non-prevent HELP
     (comfort/console/heal) -> HELP (both of which the current frame-list organ ABSTAINS on), perception
     verbs -> ABSTAIN, inanimate -> NA.
  W2 OFF-DIAGONAL (force structure does non-redundant work): ENABLE-a-bad -> HARM, PREVENT-a-good ->
     HARM, failed/negated harm -> neutral -- where a bare valence-lookup (valence_only) FAILS.
  W3 GENERALIZATION > FLOOR: on the social/emotional verbs the frame list misses, fd_arithmetic beats
     the current organ, CI-separated (paired: organ scores ~0).
  W4 AFFECTEDNESS GATE EARNS PRECISION: valence_only over-fires on perception verbs; fd_arithmetic does not.
  W5 LIVE READER: a modern social-harm sentence (mugged) and an emotional-help sentence (comforted)
     surface affect==HARM/HELP through the REAL reader (impossible for the frame list), a perception
     sentence stays out of {HARM,HELP}, and a non-affect dimension is byte-identical to the current reader.
  W6 INFO-FREE TWIN LOSES: scrambled valence + force lexicon collapses accuracy below the real arithmetic.

Run: .venv/Scripts/python.exe verification/test_fd_harm_help_arithmetic.py
"""
import glob
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import hdlab.situation_reader as SR
import hdlab.force_dynamics_valence as FDV
import experiments.exp_assembled_reader_all_flags_on_v1 as H
import experiments.exp_fd_harm_help_arithmetic_v1 as A
import experiments.exp_fd_harm_help_live_modern_v1 as LIVE

_ORIG = FDV.harm_help   # the LIVE organ (== the arithmetic since the 2026-09-12 landing); restored after monkeypatch arms


def _LEGACY(verb, animacy):
    """FROZEN copy of the PRE-landing organ decision (verb-LIST membership: FrameNet harm frames + hand backoff;
    PREVENT/ENABLE -> HELP) -- the floor this witness measures the arithmetic against. Kept HERE (test-time only);
    the read path no longer carries it."""
    global _LEG_SET
    if animacy == "inanimate":
        return "NA"
    v = FDV.lemmatize_verb(verb)
    try:
        _LEG_SET
    except NameError:
        hv = {"choke", "clobber", "wallop", "strangle", "throttle", "bite", "stomp", "shoot", "kill", "bludgeon", "wrench"}
        try:
            from nltk.corpus import framenet as fn
            for fr in ("Cause_harm", "Cause_impact", "Impact", "Killing", "Hit_target", "Cause_to_fragment", "Attack"):
                try:
                    f = fn.frame_by_name(fr)
                except Exception:
                    continue
                for lu in f.lexUnit.keys():
                    if lu.endswith(".v"):
                        b = lu.rsplit(".", 1)[0].strip().lower()
                        if b.isalpha():
                            hv.add(b)
        except Exception:
            pass
        _LEG_SET = hv
    if v in _LEG_SET:
        return "HARM"
    if FDV._lex().get(v) in ("PREVENT", "ENABLE"):
        return "HELP"
    return None


def _reader_affect(reader, toks, patient_head):
    d = os.path.join(REPO, "data", "exp_fd_harm_help_arithmetic_live_v1")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "_witness.conll")
    open(p, "w", encoding="utf-8").write(LIVE.make_conll("witness", [toks]))
    sm = reader.read(p)
    for e in sm.events:
        if e.patient and str(e.patient).lower().strip(".,") == patient_head.lower():
            return e.affect
    return None


def test_fd_harm_help_arithmetic():
    results = []

    def chk(name, cond, detail=""):
        results.append(cond)
        print(f"  {'ok' if cond else 'XX'}  {name}{('  -- ' + detail) if detail else ''}")

    hh = A.harm_help_arithmetic
    # ---- W1 DECISION -----------------------------------------------------------------------------
    w1 = all(hh(v, "animate") == "HARM" for v in ("stab", "punch", "beat", "kick", "wound")) \
        and all(hh(v, "animate") == "HELP" for v in ("save", "protect", "shield", "free", "release")) \
        and all(hh(v, "animate") == "HARM" for v in ("mug", "evict", "bully", "humiliate", "abuse")) \
        and all(hh(v, "animate") == "HELP" for v in ("comfort", "console", "heal", "cure", "feed")) \
        and all(hh(v, "animate") is None for v in ("watch", "greet", "describe", "phone")) \
        and all(hh(v, "inanimate") == "NA" for v in ("stab", "protect"))
    chk("W1 force-struct x valence: harm-frame+social->HARM, prevent+emotional->HELP, "
        "perception->abstain, inanimate->NA", w1)
    # the current frame-list organ ABSTAINS on the social/emotional verbs (the generalization gap)
    chk("W1b the PRE-landing organ (frozen frame list) abstained on all social/emotional harm+help (the gap this closes)",
        all(_LEGACY(v, "animate") is None for v in
            ("mug", "evict", "bully", "humiliate", "comfort", "console", "heal")))

    # ---- W2 OFF-DIAGONAL (force structure vs valence-lookup) --------------------------------------
    w2 = (hh("let", "animate", endstate_reached=True, embedded_endstate_valence=-1) == "HARM"
          and hh("block", "animate", endstate_reached=False, embedded_endstate_valence=+1) == "HARM"
          and hh("stab", "animate", endstate_reached=False) is None
          and hh("save", "animate", endstate_reached=False, embedded_endstate_valence=-1) == "HELP")
    val_fails = (A.valence_only("let", "animate") != "HARM"
                 or A.valence_only("stab", "animate") == "HARM")
    chk("W2 off-diagonal: ENABLE-bad->HARM, PREVENT-good->HARM, failed-harm->neutral; valence-lookup fails",
        w2 and val_fails)

    # ---- W3 GENERALIZATION > FLOOR (paired on the social/emotional verbs) -------------------------
    gen = [(v, "HARM") for v in A.P_SOCIAL_HARM] + [(v, "HELP") for v in A.P_NONPREVENT_HELP]
    fd_c = [1 if A._correct(hh(v, "animate"), g) else 0 for v, g in gen]
    org_c = [1 if A._correct(_LEGACY(v, "animate"), g) else 0 for v, g in gen]
    fd_m, fd_h = A.boot_ci(fd_c)
    org_m, org_h = A.boot_ci(org_c)
    chk("W3 generalization: fd beats the pre-landing frame-list organ CI-separated on the frame-list misses",
        (fd_m - fd_h) > (org_m + org_h),
        f"fd={fd_m:.3f}+/-{fd_h:.3f} vs organ={org_m:.3f}+/-{org_h:.3f}")

    # ---- W4 AFFECTEDNESS GATE EARNS PRECISION ----------------------------------------------------
    neutral = A.P_NEUTRAL
    fd_prec = sum(1 for v in neutral if hh(v, "animate") in (None, "NA")) / len(neutral)
    val_prec = sum(1 for v in neutral if A.valence_only(v, "animate") in (None, "NA")) / len(neutral)
    chk("W4 affectedness gate: fd keeps perception-verb precision where valence_only collapses",
        fd_prec == 1.0 and val_prec < 0.5, f"fd_prec={fd_prec:.2f} valence_only_prec={val_prec:.2f}")

    # ---- W5 LIVE READER (surface + no-regress) ---------------------------------------------------
    try:
        FDV.harm_help = lambda verb, animacy: A.harm_help_arithmetic(verb, animacy)
        reader = SR.SituationReader()
        harm_live = _reader_affect(reader, ["A", "robber", "mugged", "the", "pedestrian", "."], "pedestrian")
        help_live = _reader_affect(reader, ["A", "nurse", "comforted", "the", "patient", "."], "patient")
        perc_live = _reader_affect(reader, ["A", "clerk", "greeted", "the", "customer", "."], "customer")
        chk("W5 live: social-harm 'mugged'->HARM + emotional-help 'comforted'->HELP surface through the "
            "real reader (impossible for the frame list); perception 'greeted' stays out of {HARM,HELP}",
            harm_live == "HARM" and help_live == "HELP" and perc_live not in ("HARM", "HELP"),
            f"mugged={harm_live} comforted={help_live} greeted={perc_live}")
        # no-regress: a non-affect dimension is byte-identical between current organ and fd arithmetic
        docs = sorted(glob.glob(os.path.join(REPO, "data", "tmp_mid", "*.conll")))[:4]
        noregress = True
        for path in docs:
            FDV.harm_help = _ORIG
            s0 = H.dim_signatures(reader.read(path))
            FDV.harm_help = lambda verb, animacy: A.harm_help_arithmetic(verb, animacy)
            s1 = H.dim_signatures(reader.read(path))
            if s0 != s1:
                noregress = False
                break
        chk("W5b live no-regress: every NON-affect SituationModel dimension byte-identical on modern docs",
            noregress and bool(docs))
    finally:
        FDV.harm_help = _ORIG

    # ---- W7 COMPOSED GENERALIZATION TO REAL SYNTAX (parse-driven off-diagonal) --------------------
    import experiments.exp_fd_harm_help_composed_v1 as C
    cr = C.run()
    comp = cr["composed"]["acc"]
    bare = cr["bare_svo"]["acc"]
    # count off-diagonal cells composed recovers that bare (matrix-verb-only) gets wrong
    off_gain = sum(1 for r in cr["rows"]
                   if r["composed"] == r["gold"] and r["bare_svo"] != r["gold"])
    chk("W7 composed (parse + embedded endstate) generalizes the off-diagonal force cells to real "
        "prose, beating the matrix-verb-only arithmetic", comp > bare and off_gain >= 4,
        f"composed={comp:.3f} bare={bare:.3f} off-diagonal recovered={off_gain}")

    # ---- W6 INFO-FREE TWIN LOSES -----------------------------------------------------------------
    scr_afx = A.scramble_valence(A._AFX, A.SEED + 1)
    scr_lex = A.scramble_lexicon(A._LEX, A.SEED + 2)
    battery = [("mug", "HARM"), ("evict", "HARM"), ("bully", "HARM"), ("stab", "HARM"),
               ("comfort", "HELP"), ("heal", "HELP"), ("save", "HELP"), ("protect", "HELP")]
    real_ok = sum(1 for v, g in battery if hh(v, "animate") == g)
    twin_ok = sum(1 for v, g in battery
                  if A.harm_help_arithmetic(v, "animate", lexicon=scr_lex, afx=scr_afx) == g)
    chk("W6 info-free twin (scrambled valence + force lexicon) loses to the real arithmetic",
        twin_ok < real_ok, f"real={real_ok}/{len(battery)} twin={twin_ok}/{len(battery)}")

    npass = sum(1 for c in results if c)
    print(f"\n{npass}/{len(results)} PASS")
    return npass == len(results)


if __name__ == "__main__":
    raise SystemExit(0 if test_fd_harm_help_arithmetic() else 1)
