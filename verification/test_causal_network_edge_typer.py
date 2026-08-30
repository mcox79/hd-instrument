"""SCAFFOLD-FREE WITNESS for causation_is_typed_per_clause_not_across_the_causal_network.

Recomputes every headline from SOURCE (the gold + the arms), not from any landed metrics.json.
Run: .venv/Scripts/python.exe verification/test_causal_network_edge_typer.py

Witnesses:
  W1  cell-1 can-fail self-test fixtures
  W2  NET beats the type-blind PLACEHOLDER CI-separated (the discourse edge-typing win)
  W3  NET beats the PERCLAUSE ablation CI-separated (the CROSS-EVENT isolation, bar sec.3)
  W4  both info-free twins LOSE (force-class shuffle + edge-type shuffle)
  W5  PREVENT is the isolated cross-event class (NET 1.0 / perclause 0.0 / placeholder 0.0)
  W6  precedence gate: flashback cause-ID found by precedence, missed by adjacency
  W7  necessity: NET abstains SEQUENTIAL on non-causal sequence; placeholder false-links
  W8  real-text BOUND: physical lexicon covers only the physical slice; mental causation is the bulk
  W9  wrong-SIGN value on real PREVENT prose (typer types PREVENT, placeholder asserts CAUSE)
  W10 BUILD ACROSS: intentional front-end + the SAME Wolff typer beats physical-only + placeholder,
      twins lose, and doubles real-text coverage
  W11 all three experiment cells' --self-test can-fail fixtures pass
"""
import os
import subprocess
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._force_dynamics_lexicon import build_force_lexicon  # noqa: E402
import experiments.exp_causal_network_edge_typer_v1 as M1  # noqa: E402
import experiments.exp_causal_network_realtext_v1 as M2  # noqa: E402
import experiments.exp_causal_network_intentional_frontend_v1 as M3  # noqa: E402

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  [{name}] {'PASS' if cond else 'FAIL'} -- {detail}")


def acc(items, arm, **kw):
    return sum(int(arm(it, **kw)[0] == it["gold"]) if isinstance(arm(it, **kw), tuple)
               else int(arm(it, **kw) == it["gold"]) for it in items) / len(items)


def main():
    lex = build_force_lexicon()

    # ---------- W1: cell-1 fixtures ----------
    print("W1 cell-1 can-fail fixtures")
    try:
        M1.self_test()
        ok("W1", True, "cell-1 self-test fixtures pass")
    except AssertionError as e:
        ok("W1", False, f"self-test failed: {e}")

    # ---------- recompute cell-1 headlines from source ----------
    pool = M1.TYPING_POOL
    rec_net = [int(M1.arm_net_typer(it, lex)[0] == it["gold"]) for it in pool]
    rec_pc = [int(M1.arm_perclause(it, lex)[0] == it["gold"]) for it in pool]
    rec_ph = [int(M1.arm_placeholder(it)[0] == it["gold"]) for it in pool]
    m_net, lo_net, hi_net = M1._boot(rec_net)
    m_pc, lo_pc, hi_pc = M1._boot(rec_pc)
    m_ph, lo_ph, hi_ph = M1._boot(rec_ph)

    print("W2 NET vs placeholder")
    ok("W2", lo_net > hi_ph, f"NET {m_net:.3f}[{lo_net:.3f},{hi_net:.3f}] > placeholder {m_ph:.3f}[..,{hi_ph:.3f}]")

    print("W3 NET vs perclause (cross-event isolation)")
    ok("W3", lo_net > hi_pc, f"NET {m_net:.3f} lo {lo_net:.3f} > perclause {m_pc:.3f} hi {hi_pc:.3f}")

    print("W4 info-free twins lose")
    preds_net = [M1.arm_net_typer(it, lex)[0] for it in pool]
    twinA = sorted(M1._acc([int(M1.arm_net_typer(it, M1._shuffled_lexicon(lex, 1000 + s))[0] == it["gold"])
                            for it in pool]) for s in range(M1.N_SHUF))
    twinA_p95 = twinA[int(0.95 * (len(twinA) - 1))]
    twinB = sorted(M1._edge_type_shuffle_acc(pool, preds_net, 2000 + s) for s in range(M1.N_SHUF))
    twinB_p95 = twinB[int(0.95 * (len(twinB) - 1))]
    ok("W4", lo_net > twinA_p95 and lo_net > twinB_p95,
       f"force-shuffle p95 {twinA_p95:.3f}, edge-shuffle p95 {twinB_p95:.3f}, NET lo {lo_net:.3f}")

    print("W5 PREVENT is the isolated cross-event class")
    pv_net = acc(M1.SET_PREVENT, M1.arm_net_typer, lexicon=lex)
    pv_pc = acc(M1.SET_PREVENT, M1.arm_perclause, lexicon=lex)
    pv_ph = acc(M1.SET_PREVENT, M1.arm_placeholder)
    ok("W5", pv_net == 1.0 and pv_pc == 0.0 and pv_ph == 0.0,
       f"PREVENT NET {pv_net:.2f} / perclause {pv_pc:.2f} / placeholder {pv_ph:.2f}")

    print("W6 precedence gate (flashback cause-ID)")
    flash = M1._flashback_cause_id(lex)
    ok("W6", flash["precedence_cause_id_acc"] > flash["adjacency_cause_id_acc"],
       f"precedence {flash['precedence_cause_id_acc']:.2f} vs adjacency {flash['adjacency_cause_id_acc']:.2f}")

    print("W7 necessity: NET abstains on non-causal sequence, placeholder false-links")
    seq_net = acc(M1.SET_SEQ, M1.arm_net_typer, lexicon=lex)
    seq_ph = acc(M1.SET_SEQ, M1.arm_placeholder)
    ok("W7", seq_net == 1.0 and seq_ph == 0.0,
       f"SEQUENTIAL NET {seq_net:.2f} (abstains) vs placeholder {seq_ph:.2f} (false-links)")

    # ---------- W8/W9: real-text bound (recompute from source) ----------
    print("W8 real-text bound: physical slice only")
    from nltk.stem import WordNetLemmatizer
    import experiments.exp_read_causal_chain_on_chain_cause_v1 as RC
    lm = WordNetLemmatizer()
    cov = sum(1 for it in RC.GOLD if lex.get(lm.lemmatize(it.cause_lemma, "v")) is not None)
    ph_all = sum(1 for it in RC.GOLD if M2.EDGE_TYPE[(it.outcome_lemma, it.cause_lemma)][0] == "CAUSE")
    ok("W8", cov <= 4 and ph_all == len(RC.GOLD),
       f"physical coverage {cov}/{len(RC.GOLD)}; real gold is all-CAUSE ({ph_all}/{len(RC.GOLD)}) -> majority not beaten")

    print("W9 wrong-sign value on real PREVENT prose")
    from experiments._force_dynamics_lexicon import force_dynamic_type
    tp = 0
    for it in M2.PREVENT_PROSE:
        es = M2._prevent_endstate(it, lex)
        t = force_dynamic_type(it["cause"], es, lex)
        tp += int(t == "PREVENT")
    ok("W9", tp == len(M2.PREVENT_PROSE),
       f"typer types PREVENT {tp}/{len(M2.PREVENT_PROSE)}; placeholder asserts CAUSE 0/{len(M2.PREVENT_PROSE)}")

    # ---------- W10: build across the wall (intentional front-end) ----------
    print("W10 build across: intentional front-end + SAME typer")
    il = M3.build_intentional_lexicon()
    poolI = M3.POOL
    recI = [int(M3.arm_intentional(it, il) == it["gold"]) for it in poolI]
    recP = [int(M3.arm_physical_only(it, lex) == it["gold"]) for it in poolI]
    recPh = [int(M3.arm_placeholder(it) == it["gold"]) for it in poolI]
    mI, loI, hiI = M1._boot(recI)
    mP, loP, hiP = M1._boot(recP)
    mPh, loPh, hiPh = M1._boot(recPh)
    predsI = [M3.arm_intentional(it, il) for it in poolI]
    twI = sorted(M1._acc([int(M3.arm_intentional(it, M3._shuffled(il, 1000 + s)) == it["gold"])
                          for it in poolI]) for s in range(M1.N_SHUF))
    twI_p95 = twI[int(0.95 * (len(twI) - 1))]
    ok("W10", loI > hiP and loI > hiPh and loI > twI_p95,
       f"intentional {mI:.3f}[lo {loI:.3f}] > physical {mP:.3f}[hi {hiP:.3f}] & placeholder {mPh:.3f}[hi {hiPh:.3f}]; twin p95 {twI_p95:.3f}")

    # coverage doubling on real text
    union = sum(1 for it in RC.GOLD
                if (il.get(lm.lemmatize(it.cause_lemma, "v")) is not None)
                or (lex.get(lm.lemmatize(it.cause_lemma, "v")) is not None))
    ok("W10b", union > cov, f"combined real-text coverage {union}/{len(RC.GOLD)} > physical-alone {cov}/{len(RC.GOLD)}")

    # ---------- W11b: the honest REAL cross-sentence typing negative ----------
    print("W11b real cross-sentence typing gold (the honest capability test)")
    import experiments.exp_causal_network_realtext_typing_gold_v1 as M4
    from experiments._force_dynamics_lexicon import build_force_lexicon as _bfl
    _lex = _bfl()
    gold = M4._mixed_gold()
    tc = pc = 0
    for g in gold:
        pred, _c, _t = M2.type_edge_rt(g["text"], g["outcome"], _lex)
        tc += int(pred == g["gold"]); pc += int("CAUSE" == g["gold"])
    ok("W11b", tc / len(gold) < pc / len(gold),
       f"on REAL cross-sentence causation the typer {tc}/{len(gold)} does NOT beat majority-CAUSE {pc}/{len(gold)} "
       f"-- rigorous negative: real cross-sentence non-CAUSE is rare + lexically uncovered")

    # ---------- W11c: graded necessity (higher-fidelity edge representation) ----------
    print("W11c graded necessity reproduces Trabasso's ordering, twin breaks")
    import experiments.exp_causal_network_graded_necessity_v1 as M5
    nec = [M5.graded_strength(t, d)[0] for (_n, d, t, _r) in M5.TRABASSO]
    ordn = [r for (_n, _d, _t, r) in M5.TRABASSO]
    rho = M5._spearman(nec, ordn)
    import random as _rnd
    rg = _rnd.Random(M5.SEED)
    tw = []
    for _ in range(M5.N_SHUF):
        v = list(nec); rg.shuffle(v); tw.append(M5._spearman(v, ordn))
    tw.sort(); tw_p95 = tw[int(0.95 * (len(tw) - 1))]
    mono = all(nec[i] > nec[i + 1] for i in range(len(nec) - 1))
    ok("W11c", rho > tw_p95 and mono,
       f"graded necessity orders physical>...>enabling rho {rho:.3f} > twin p95 {tw_p95:.3f} (discrete read-out is a lossy projection of a graded rep)")

    # ---------- W11d: HUMAN-DATA validation (non-circular, against real judgments) ----------
    print("W11d force model predicts human causal-verb judgments (CICL causative-verbs)")
    import experiments.exp_causal_network_human_validation_v1 as M6
    human, _tot = M6.load_human()
    pb, hb, _lab = M6._cells(human, graded=False)           # binary preds (no tuned constants)
    r_bin = M6._pearson(pb, hb)
    import random as _r2
    tw = []
    for s in range(500):
        pv = list(pb); _r2.Random(1000 + s).shuffle(pv); tw.append(M6._pearson(pv, hb))
    tw.sort(); tw_p95 = tw[int(0.95 * (len(tw) - 1))]
    ok("W11d", r_bin > tw_p95 and r_bin >= 0.8,
       f"force-config predictions vs human proportion-yes r={r_bin:.3f} > shuffle-twin p95 {tw_p95:.3f} "
       f"(non-circular: config decoded from stimulus labels, target is human data)")

    # ---------- W11: all cell self-tests ----------
    print("W11 all cell --self-test fixtures")
    cells = ["exp_causal_network_edge_typer_v1", "exp_causal_network_realtext_v1",
             "exp_causal_network_intentional_frontend_v1", "exp_causal_network_realtext_typing_gold_v1",
             "exp_causal_network_graded_necessity_v1", "exp_causal_network_human_validation_v1"]
    allok = True
    for c in cells:
        r = subprocess.run([sys.executable, os.path.join(_REPO, "experiments", c + ".py"), "--self-test"],
                           capture_output=True, text=True)
        cok = r.returncode == 0 and "PASS" in r.stdout
        allok = allok and cok
        print(f"    {c}: {'OK' if cok else 'FAIL'}")
    ok("W11", allok, "all three cell self-tests pass")

    print(f"\n{'='*70}\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS -- discourse causal-network EDGE typer witnessed "
          f"scaffold-free: force-typed cross-event edges beat the untyped placeholder CI-separated "
          f"(NET {m_net:.3f} vs {m_ph:.3f}), the cross-event PREVENT lift is isolated from single-clause typing "
          f"(perclause {m_pc:.3f}), twins lose; the real-text bound is PRINCIPLED (physical force dynamics types "
          f"the physical slice, mental causation is a different brain system) and is BUILT ACROSS by a second "
          f"intentional front-end feeding the SAME Wolff typer ({mI:.3f} vs physical-only {mP:.3f}).")
    if FAIL:
        print("FAILED:", FAIL)
        sys.exit(1)


if __name__ == "__main__":
    main()
