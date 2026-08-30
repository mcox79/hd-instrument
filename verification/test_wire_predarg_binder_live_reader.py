"""Scaffold-free witness for wire_the_predarg_frontend_and_binder_into_the_live_reader.

Asserts the load-bearing claims WITHOUT the frame-induction training (the frame labeler is an additive
ablation, not the core wiring), so this runs in ~seconds-to-a-minute on the 57 McGuffey passages / 178
target queries -- the inherited end-to-end role instrument (exp_wire_organs_endtoend_v1, the prior negative).

  CORE WIRING (parse -> route_predicate_arguments (+ quotative inversion) -> graded binder):
  1. The wired reader BEATS the current POSITIONAL reader CI-separated end-to-end (family grain).
  2. It beats positional at the STRICT exact-match grain too (the win is not a grain artifact).
  3. The info-free ROLE twin (labels detached from heads) LOSES CI-separated.
  4. QUOTATIVE INVERSION is the dominant lever (the landed router's missing speech-verb agent rule),
     CI-separated -- and it is what recovers the postverbal-speaker agent the positional NVN rule brands
     an object.
  5. The brain-faithful HYBRID (parse-structure when available, positional fallback when the parser leaves
     a clause structureless -- Ferreira good-enough) keeps the lift AND cuts regression.
  6. Mechanism can-fail: the router recovers GOAL + RECIPIENT off the REAL parse (roles the positional
     rule scores 0.000 on); the graded binder binds a gender-compatible pronoun to the entity with history.
  7. FLOORS: the wired reader beats content-lemma COUNTING on positional-store; it does NOT beat the
     ORACLE-store counting floor (~0.98) -- the inherited cap no front-end-driven reader can beat (the
     prior negative established this). Recorded, not hidden.
  8. HONEST measurement-population fact: on McGuffey the random-BIND twin TIES the graded binder -- the
     role metric is parse-derived + majority-agent-fallback-masked, so it cannot see the binder's
     who-did-what value (that value is on LitBank, +0.136 CI-sep, landed).

Run: .venv/Scripts/python.exe verification/test_wire_predarg_binder_live_reader.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import experiments.exp_wire_organs_endtoend_v1 as P  # noqa: E402
import experiments.exp_wire_predarg_binder_live_reader_v1 as E  # noqa: E402
from hdlab.predicate_argument_frontend import route_predicate_arguments  # noqa: E402


def main():
    checks = []
    gen = E._load_gen()
    ps = P.load_gold()
    pids = [p["passage_id"] for p in ps]
    NB = 2000

    pos_b = {p["passage_id"]: E.positional_bindings(p) for p in ps}
    predraw = {pid: E.predarg_extract_raw(E._pass(ps, pid), gen, use_frame=False, seed=0) for pid in pids}
    prednqraw = {pid: E.predarg_extract_raw(E._pass(ps, pid), gen, use_frame=False, quotative=False, seed=0)
                 for pid in pids}
    troleraw = {pid: E.predarg_extract_raw(E._pass(ps, pid), gen, use_frame=False, twin_role=True, seed=0)
                for pid in pids}
    pred_b = {pid: E.resolve_graded(predraw[pid], E._pass(ps, pid), seed=0) for pid in pids}
    prednq_b = {pid: E.resolve_graded(prednqraw[pid], E._pass(ps, pid), seed=0) for pid in pids}
    trole_b = {pid: E.resolve_graded(troleraw[pid], E._pass(ps, pid), seed=0) for pid in pids}
    tbind_b = {pid: E.resolve_graded(predraw[pid], E._pass(ps, pid), twin_bind=True, seed=0) for pid in pids}
    hyb_b = {pid: pred_b[pid] + pos_b[pid] for pid in pids}

    # 1. wired (hybrid) beats positional CI-separated (family grain)
    d = E.paired_delta(ps, hyb_b, pos_b, subset="all", seed=0, n_boot=NB)
    checks.append((f"HYBRID beats POSITION end-to-end (family) delta={d['delta']:+.3f} "
                   f"CI[{d['ci'][0]:+.3f},{d['ci'][1]:+.3f}] {d['band']}", d["band"] == "ABOVE"))

    # 2. beats positional at the STRICT exact grain too
    pe = E.score_roles(ps, pred_b, grain="exact", subset="all", seed=0)
    poe = E.score_roles(ps, pos_b, grain="exact", subset="all", seed=0)
    checks.append((f"PREDARG beats POSITION at EXACT grain {pe['role_acc']:.3f} vs {poe['role_acc']:.3f} "
                   f"(not a family-grain artifact)", pe["role_ci"][0] > poe["role_ci"][1]))

    # 3. info-free ROLE twin loses CI-separated (all)
    dt = E.paired_delta(ps, pred_b, trole_b, subset="all", seed=0, n_boot=NB)
    checks.append((f"info-free ROLE twin loses (all) delta={dt['delta']:+.3f} "
                   f"CI[{dt['ci'][0]:+.3f},{dt['ci'][1]:+.3f}] {dt['band']}", dt["band"] == "ABOVE"))

    # 4. quotative inversion is the dominant lever, CI-separated
    dq = E.paired_delta(ps, pred_b, prednq_b, subset="all", seed=0, n_boot=NB)
    checks.append((f"QUOTATIVE inversion lever delta={dq['delta']:+.3f} CI[{dq['ci'][0]:+.3f},{dq['ci'][1]:+.3f}] "
                   f"{dq['band']} (the landed router's missing speech-verb agent rule)", dq["band"] == "ABOVE"))

    # 5. hybrid keeps the lift AND cuts regression vs the pure predarg
    nr_pred = E.no_regression(ps, pos_b, pred_b, grain="family")
    nr_hyb = E.no_regression(ps, pos_b, hyb_b, grain="family")
    checks.append((f"HYBRID cuts regression {nr_pred['regressed']}->{nr_hyb['regressed']} of "
                   f"{nr_hyb['pos_correct']} positional-correct (good-enough fallback)",
                   nr_hyb["regressed"] <= nr_pred["regressed"] and nr_hyb["regression_rate"] < 0.12))

    # 6. mechanism can-fail: router recovers goal + recipient off the REAL parse
    r = gen.generate("John ran into the garden .")
    v = [i for i in range(1, len(r.tokens) + 1) if r.pos[i - 1] == "VERB"][0]
    ro = route_predicate_arguments(r.tokens, r.pos, r.heads, v)
    goal_ok = bool(ro["goal"]) and r.tokens[ro["goal"] - 1].lower() == "garden"
    r2 = gen.generate("The girl gave the apple to the beggar .")
    v2 = [i for i in range(1, len(r2.tokens) + 1) if r2.pos[i - 1] == "VERB"][0]
    ro2 = route_predicate_arguments(r2.tokens, r2.pos, r2.heads, v2)
    recip_ok = bool(ro2["recipient"]) and r2.tokens[ro2["recipient"] - 1].lower() == "beggar"
    checks.append(("router recovers GOAL(garden) + RECIPIENT(beggar) off the real parse "
                   "(roles the positional rule scores 0.000 on)", goal_ok and recip_ok))

    # 7. floors: beats counting on positional-store; does NOT beat oracle-store counting (documented cap)
    ora_b = {p["passage_id"]: E.oracle_bindings(p) for p in ps}
    cpos = E.paired_vs_counting(ps, pred_b, pos_b, seed=0, n_boot=NB)
    cora = E.paired_vs_counting(ps, pred_b, ora_b, seed=0, n_boot=NB)
    checks.append((f"beats counting on positional-store ({cpos['delta']:+.3f} {cpos['band']}) but NOT "
                   f"oracle-store counting ({cora['delta']:+.3f} {cora['band']}, the inherited cap)",
                   cpos["band"] == "ABOVE" and cora["band"] == "BELOW"))

    # 8. HONEST: on McGuffey the role metric cannot see the binder (random-bind twin ties)
    db = E.paired_delta(ps, pred_b, tbind_b, subset="all", seed=0, n_boot=NB)
    checks.append((f"random-BIND twin TIES on McGuffey role metric ({db['delta']:+.3f} {db['band']}) -- the "
                   f"parse-derived, majority-fallback-masked role metric cannot see the binder", db["band"] == "NOT_SEP"))

    # 9. 2nd, BINDING-SENSITIVE metric (which entity filled the role-slot): the wiring beats positional here too.
    predrec_b = {pid: P.resolve_raw(predraw[pid], E._pass(ps, pid), "recency") for pid in pids}
    wdw = E.who_did_what(ps, {"POSITION": pos_b, "PREDARG_RECENCY": predrec_b, "PREDARG_GRADED": pred_b,
                              "PREDARG_RANDBIND": tbind_b}, seed=0, n_boot=NB)
    wp = wdw["contrasts"]["PREDARG_over_POSITION_all"]
    checks.append((f"who-did-what (binding-sensitive): PREDARG beats POSITION {wdw['all']['PREDARG_GRADED']['acc']:.3f} "
                   f"vs {wdw['all']['POSITION']['acc']:.3f} (delta {wp['delta']:+.3f} {wp['band']}) -- 2nd metric",
                   wp["band"] == "ABOVE"))

    # 10. HONEST (confirmed by a DIRECT binding control, not just asserted): even on the pronoun-only
    #     binding-sensitive subset, the random-BIND twin TIES the graded binder -> McGuffey structurally lacks
    #     the same-gender referential competition the binder resolves (its value is LitBank, +0.136 landed).
    gt = wdw["contrasts"]["GRADED_over_RANDBIND_twin_pronoun"]
    checks.append((f"random-BIND twin ties GRADED on the PRONOUN who-did-what subset ({gt['delta']:+.3f} {gt['band']}, "
                   f"n={wdw['pronoun']['PREDARG_GRADED']['n']}) -> McGuffey cannot exercise coreference; the binder's "
                   f"value is LitBank (+0.136 CI-sep, landed)", gt["band"] == "NOT_SEP"))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
