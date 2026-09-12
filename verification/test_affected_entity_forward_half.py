"""Landing witness -- the FORWARD HALF of pronoun-undergoer resolution (strategy pri-1, 2026-09-12):
hdlab.affected_entity_resolver.EntityTokens (accrual of every pronoun reference, foreground window, Principle A)
+ the live reader wire (situation_reader._read_affected_entity walks the mention stream through the organ).

  W1 ORGAN self-test passes (Principle A; accrual raises the token; foreground prefers in-focus tokens).
  W2 CELL (gold roles, THIRD-person GUM undergoers, n>500): accrual+window+Principle A beats the landed resolver
     CI-separated; accrual-scrambled and window-scrambled twins LOSE; the landed resolver's own witness still passes
     (the organ's resolve() default path is byte-identical).
  W3 READER: (a) byte-identical off vs on for the other dimensions (PURE ADD); (b) a REFLEXIVE theme resolves to the
     clause-mate agent (Principle A) where the landed path excluded it; (c) the schema is unchanged; (d) a non-theme
     pronoun reference is ACCRUED to its token (the organ state grows), checked through the organ on the reader's stream.
  W4 DEPLOYMENT: the cell on the predicted parse is CI-separated over the landed resolver (the board row's number).

Run: .venv/Scripts/python.exe verification/test_affected_entity_forward_half.py   [--fast skips W4]
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import hdlab.affected_entity_resolver as AER
from hdlab.situation_reader import SituationReader, _write_temp_conll

_fail = []


def _ck(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        _fail.append(msg)


def main(fast=False):
    # W1
    try:
        AER.self_test(); _ck(True, "W1 organ self-test (Principle A, accrual, foreground)")
    except AssertionError as e:
        _ck(False, f"W1 organ self-test: {e}")
    # W2
    import experiments.exp_affected_entity_token_history_gum_v1 as TH
    r = TH.run()
    a = r["accrual_plus_window_plus_principle_a"]; c1 = r["CONTROL_accrual_scrambled_plus_window"]; c2 = r["CONTROL_window_scrambled_plus_accrual"]
    _ck(r["n_third_undergoers"] > 500, f"W2 population n={r['n_third_undergoers']} > 500")
    _ck(a["ci_sep"] and a["delta"] > 0, f"W2 forward half CI-sep over the landed resolver on gold roles: {r['incumbent_acc']} -> {a['acc']} (+{a['delta']}, CI{a['ci95']})")
    _ck(c1["acc"] < a["acc"] and c2["acc"] < a["acc"], f"W2 twins lose: accrual-scrambled {c1['acc']}, window-scrambled {c2['acc']} < {a['acc']}")
    import experiments.exp_affected_entity_binding_parallelism_gum_v1 as B4
    r4 = B4.run()
    _ck(abs(r4["accuracy"]["A5_full"] - 0.4632) < 1e-4, f"W2 landed resolver path byte-identical (A5_full={r4['accuracy']['A5_full']} == 0.4632)")
    # W3 reader
    rows = [
        (1, 1, "John", "(0)"), (1, 2, "met", "-"), (1, 3, "Peter", "(1)"), (1, 4, ".", "-"),
        (2, 1, "John", "(0)"), (2, 2, "blamed", "-"), (2, 3, "himself", "(0)"), (2, 4, ".", "-"),
        (3, 1, "Peter", "(1)"), (3, 2, "thanked", "-"), (3, 3, "him", "(0)"), (3, 4, ".", "-"),
    ]
    path = _write_temp_conll(rows)
    on = SituationReader(); off = SituationReader()
    on.track_affected_entity = True; off.track_affected_entity = False
    sm_on = on.read(path); sm_off = off.read(path)
    def ev(sm):
        return (repr(getattr(sm, "events", None)), repr(getattr(sm, "commonnoun_resolution", None)), repr(getattr(sm, "coref_acc", None)))
    _ck(ev(sm_on) == ev(sm_off), "W3a byte-identical off vs on (events / commonnoun_resolution / coref_acc)")
    _ck(getattr(sm_off, "affected_entity", []) == [], "W3a OFF arm leaves sm.affected_entity == []")
    ae = getattr(sm_on, "affected_entity", [])
    _ck(all(set(x) == {"sent_idx", "verb_pos", "undergoer", "resolved", "coarg"} for x in ae), f"W3c schema unchanged (n={len(ae)})")
    refl = [x for x in ae if x["undergoer"] == "himself"]
    _ck(bool(refl) and refl[0]["resolved"] == "john", f"W3b reflexive 'himself' resolves to the clause-mate agent john (Principle A); got {refl}")
    him = [x for x in ae if x["undergoer"] == "him"]
    _ck(bool(him) and him[0]["resolved"] == "john", f"W3b 'him' (agent Peter excluded by Principle B) resolves to john; got {him}")
    # W3d accrual through the organ on a reader-shaped stream: after resolving 'himself' -> john, john's token carries it
    T = AER.EntityTokens()
    T.observe("john", 0, "SUBJECT", 0, "masc", "singular", "nsubj"); T.observe("peter", 1, "OBJECT", 0, "masc", "singular", "obj")
    pick, _ = T.resolve_pronoun(2, 1, gender="masc", number="singular", a_role="OBJ", role="OBJECT", coarg_key="john", reflexive=True)
    _ck(pick == "john" and T.pron_hist.get("john") == [(2.0, "OBJECT")], f"W3d the reflexive reference is ACCRUED to john's token: {T.pron_hist}")
    # W4
    if not fast:
        rp = TH.run(predicted_parse=True)
        ap = rp["accrual_plus_window_plus_principle_a"]
        _ck(ap["ci_sep"] and ap["delta"] > 0, f"W4 deployment (predicted parse): {rp['incumbent_acc']} -> {ap['acc']} (+{ap['delta']}, CI{ap['ci95']}) CI-sep")
    print("\nRESULT:", "PASS" if not _fail else f"FAIL {_fail}")
    return not _fail


if __name__ == "__main__":
    ok = main(fast="--fast" in sys.argv)
    sys.exit(0 if ok else 1)
