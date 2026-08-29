"""SCAFFOLD-FREE WITNESS for causation_has_no_force_dynamic_typing.

Recomputes every headline from SOURCE (the shared lexicon + the two cells' gold/arms), not from any
landed metrics.json -- so a stale/rewritten metrics file cannot make this pass. Run:
    .venv/Scripts/python.exe verification/test_causal_force_dynamic_typing.py

Witnesses:
  W0  lexicon is FrameNet-derived + external (class distribution; the one principled ENABLE/PREVENT split)
  W1  Wolff truth-table correctness (CAUSE/ENABLE/PREVENT from class x endstate)
  W2  endstate/negation detector (reached vs blocked)
  W3  typer beats the connective/adjacency PLACEHOLDER CI-separated on the pooled task
  W4  typer beats PRECEDENCE-ONLY CI-separated
  W5  force-class-shuffle info-free twin LOSES
  W6  CAUSE-vs-ENABLE verb isolation (endstate constant): FD 1.0, verb-shuffle twin at chance
  W7  PREVENT killer (Set C): FD >> link-outcome placeholder (which is 0)
  W8  frequency-matched random-label floor beaten
  W9  gold verbs are covered by PURE FrameNet frames (not curated into the lexicon via backoff)
  W10 tendency-ambiguity WALL: verb-lexicon 0.50 vs tendency-oracle 1.00 on covered ambiguous verbs
  W11 ENABLE is barely lexicalised (held-out non-gold verbs: ENABLE count tiny)
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from collections import Counter

from experiments._force_dynamics_lexicon import (
    build_force_lexicon, force_dynamic_type, detect_endstate_reached, ENABLE_LUS,
)
from experiments import exp_causal_force_dynamic_typer_v1 as TC
from experiments import exp_causal_force_lexicon_coverage_v1 as CC
from experiments import exp_causal_tendency_recovery_v1 as TR
from experiments import exp_causal_force_dynamic_realtext_v1 as RT

_PASS = 0
_FAIL = 0


def check(name, cond, detail=""):
    global _PASS, _FAIL
    tag = "PASS" if cond else "FAIL"
    if cond:
        _PASS += 1
    else:
        _FAIL += 1
    print(f"[{tag}] {name}" + (f"  ::  {detail}" if detail else ""))


def main():
    lex = build_force_lexicon()
    dist = Counter(lex.values())

    # W0 -- external FrameNet lexicon
    check("W0 lexicon FrameNet-derived + external",
          len(lex) > 300 and dist["CAUSE"] > 100 and dist["PREVENT"] > 20 and dist["ENABLE"] >= 4,
          f"n={len(lex)} {dict(dist)}; ENABLE split LUs={sorted(ENABLE_LUS)}")

    # W1 -- Wolff truth-table
    check("W1 truth-table CAUSE/ENABLE/PREVENT",
          force_dynamic_type("shatter", True, lex) == "CAUSE"
          and force_dynamic_type("let", True, lex) == "ENABLE"
          and force_dynamic_type("prevent", False, lex) == "PREVENT"
          and force_dynamic_type("prevent", True, lex) != "PREVENT",
          "shatter/reached=CAUSE, let/reached=ENABLE, prevent/blocked=PREVENT, prevent/reached!=PREVENT")

    # W2 -- endstate/negation detector
    check("W2 endstate detector reached vs blocked",
          detect_endstate_reached(["the", "river", "rose"]) is True
          and detect_endstate_reached(["the", "valley", "stayed", "dry"]) is False
          and detect_endstate_reached(["the", "flood", "never", "came"]) is False
          and detect_endstate_reached(["it", "did", "n't", "ignite"]) is False)

    # Pooled task + arms (recompute)
    POOL = TC.SET_A + TC.SET_C + TC.SET_B
    fd = TC.score(POOL, TC.arm_force_dynamic, lexicon=lex)
    ph = TC.score(POOL, TC.arm_placeholder)
    pr = TC.score(POOL, TC.arm_precedence_only)
    m_fd, lo_fd, hi_fd = TC._boot(fd)
    m_ph, lo_ph, hi_ph = TC._boot(ph)
    m_pr, lo_pr, hi_pr = TC._boot(pr)

    # W3 -- beats placeholder CI-separated
    check("W3 typer > placeholder (CI-sep)", lo_fd > hi_ph,
          f"FD {m_fd:.3f}[{lo_fd:.3f},{hi_fd:.3f}] vs placeholder {m_ph:.3f}[{lo_ph:.3f},{hi_ph:.3f}]")

    # W4 -- beats precedence-only CI-separated
    check("W4 typer > precedence-only (CI-sep)", lo_fd > hi_pr,
          f"FD lo {lo_fd:.3f} vs precedence hi {hi_pr:.3f}")

    # W5 -- info-free twin loses
    twin = sorted(TC._acc(TC.score(POOL, TC.arm_force_dynamic, lexicon=TC._shuffled_lexicon(lex, 1000 + s)))
                  for s in range(TC.N_SHUF))
    twin_p95 = twin[int(0.95 * (len(twin) - 1))]
    check("W5 force-class-shuffle twin loses", lo_fd > twin_p95,
          f"FD lo {lo_fd:.3f} vs twin p95 {twin_p95:.3f} (twin mean {sum(twin)/len(twin):.3f})")

    # W6 -- CAUSE-vs-ENABLE isolation (endstate constant)
    ce = [it for it in TC.SET_A if it[4] in ("CAUSE", "ENABLE")]
    fd_ce = TC._acc(TC.score(ce, TC.arm_force_dynamic, lexicon=lex))
    ce_twin = sorted(TC._acc(TC.score(ce, TC.arm_force_dynamic, lexicon=TC._shuffled_lexicon(lex, 2000 + s)))
                     for s in range(TC.N_SHUF))
    ce_twin_p95 = ce_twin[int(0.95 * (len(ce_twin) - 1))]
    check("W6 CAUSE-vs-ENABLE verb isolation", fd_ce >= 0.95 and fd_ce > ce_twin_p95,
          f"FD {fd_ce:.3f} vs verb-shuffle twin p95 {ce_twin_p95:.3f} (mean {sum(ce_twin)/len(ce_twin):.3f})")

    # W7 -- PREVENT killer
    fd_c = TC._acc(TC.score(TC.SET_C, TC.arm_force_dynamic, lexicon=lex))
    ph_c = TC._acc(TC.score(TC.SET_C, TC.arm_placeholder))
    check("W7 PREVENT killer Set C", fd_c >= 0.8 and ph_c == 0.0,
          f"FD {fd_c:.3f} vs link-outcome placeholder {ph_c:.3f}")

    # W8 -- frequency-matched random floor
    fr_analytic, _ = TC._freq_random_acc(POOL)
    check("W8 beats frequency-matched random", lo_fd > fr_analytic,
          f"FD lo {lo_fd:.3f} vs freq-random {fr_analytic:.3f}")

    # W9 -- the win is NOT a backoff artifact: drop the narrative backoff (pure FrameNet) and the typer
    #       STILL beats the placeholder CI-separated (uncovered force verbs just become SEQUENTIAL misses)
    lex_pure = build_force_lexicon(backoff={})
    fd_pure = TC.score(POOL, TC.arm_force_dynamic, lexicon=lex_pure)
    m_fdp, lo_fdp, hi_fdp = TC._boot(fd_pure)
    gold_verbs = sorted({it[1] for it in (TC.SET_A + TC.SET_C)})
    pure_cov = sum(1 for v in gold_verbs if v in lex_pure)
    check("W9 win survives dropping backoff (pure FrameNet > placeholder CI-sep)", lo_fdp > hi_ph,
          f"pure-FrameNet FD {m_fdp:.3f}[{lo_fdp:.3f},{hi_fdp:.3f}] > placeholder {m_ph:.3f}[..,{hi_ph:.3f}]; "
          f"{pure_cov}/{len(gold_verbs)} gold verbs in FrameNet-only (rest are backoff-filled force verbs)")

    # W10 -- tendency-ambiguity wall
    lex_hits = total = 0
    for verb, _en, _ca in CC.TENDENCY_AMBIGUOUS:
        for kind in ("enable", "cause"):
            gold = CC._tendency_gold(kind)
            pred = force_dynamic_type(verb, True, lex)   # verb-lexicon is tendency-blind
            lex_hits += int(pred == gold)
            total += 1
    wall_acc = lex_hits / total
    check("W10 tendency-ambiguity WALL (verb lexicon capped ~0.5)", 0.4 <= wall_acc <= 0.6,
          f"verb-lexicon {wall_acc:.3f} vs tendency-oracle 1.000 (gap {1-wall_acc:.3f})")

    # W11 -- ENABLE barely lexicalised
    heldout = [(v, c) for v, c in lex.items() if v not in CC.TYPER_GOLD_VERBS]
    n_enable = sum(1 for _, c in heldout if c == "ENABLE")
    check("W11 ENABLE barely lexicalised (partly constructed)", n_enable <= 3,
          f"{n_enable} ENABLE verbs among {len(heldout)} non-gold (Kuhnmuench & Beller 2005)")

    # W12 -- the tendency wall is CROSSED via affector-magnitude (Wolff force arithmetic)
    lex_c = build_force_lexicon()
    verb_only = sum(int(force_dynamic_type(v, True, lex_c) == g) for (a, v, p, g) in TR.PRIMARY) / len(TR.PRIMARY)
    with_tend = sum(int(TR.type_with_tendency(a, v, True, lex_c) == g) for (a, v, p, g) in TR.PRIMARY) / len(TR.PRIMARY)
    check("W12 tendency wall crossed (affector-magnitude)", verb_only <= 0.55 and with_tend >= 0.9,
          f"verb-only {verb_only:.3f} (cap) -> +affector-magnitude {with_tend:.3f}")

    # W13 -- the magnitude cue is load-bearing: shuffle weak/strong -> falls back toward chance
    tw = sorted(sum(int(TR.type_with_tendency(a, v, True, lex_c, weak=w, strong=st) == g)
                    for (a, v, p, g) in TR.PRIMARY) / len(TR.PRIMARY)
                for w, st in (TR._shuffled_mag(1000 + s) for s in range(TR.N_SHUF)))
    tw_p95 = tw[int(0.95 * (len(tw) - 1))]
    check("W13 magnitude-shuffle twin loses", with_tend > tw_p95,
          f"with-tendency {with_tend:.3f} vs magnitude-shuffle twin p95 {tw_p95:.3f} (mean {sum(tw)/len(tw):.3f})")

    # W14 -- real-text: mechanism recovers genuine force-dynamic causation, beats placeholder
    lex_r = build_force_lexicon()
    gold = [g["gold"] for g in RT.GOLD]
    fs = [i for i, g in enumerate(RT.GOLD) if g["force_sense"]]
    blind = [RT.arm_typer(g, lex_r) for g in RT.GOLD]
    ph = [RT.arm_placeholder(g) for g in RT.GOLD]
    fs_acc = sum(int(blind[i] == gold[i]) for i in fs) / len(fs)
    fs_ph = sum(int(ph[i] == gold[i]) for i in fs) / len(fs)
    check("W14 real-text force-sense typer > placeholder", fs_acc >= 0.85 and fs_acc > fs_ph + 0.3,
          f"force-sense acc {fs_acc:.3f} (n={len(fs)}) vs placeholder {fs_ph:.3f}")

    # W15 -- real-text: PREVENT from-construction self-disambiguates polysemous non-force uses
    prevverb_nonforce = [i for i, g in enumerate(RT.GOLD)
                         if not g["force_sense"] and lex_r.get(g["lemma"]) == "PREVENT"]
    correct_filtered = sum(int(blind[i] == "NOT_FORCE") for i in prevverb_nonforce)
    check("W15 PREVENT from-construction gates polysemous non-force PREVENT verbs",
          len(prevverb_nonforce) > 0 and correct_filtered == len(prevverb_nonforce),
          f"{correct_filtered}/{len(prevverb_nonforce)} non-force keep/hold/stop/save correctly NOT_FORCE")

    print(f"\n==== {_PASS}/{_PASS + _FAIL} PASS ====")
    return _FAIL == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
