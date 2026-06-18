"""Self-test for the 3rd self-cert gate (working-baseline-cliff). Skunkworks 2026-06-18.
Verifies: producer baseline_cliff_self_check (deterministic is_working_baseline_cliff from measured low/high),
consumer baseline_cliff_gate (forces NON_TEST iff field present AND is_working_baseline_cliff==False),
composition with discrimination_gate, and NON-RETROACTIVITY (no field -> verdict unchanged). ASCII; no LLM."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments._cell_provenance import baseline_cliff_self_check, corpus_completeness_self_check
from tools.atomize_experiment_records import baseline_cliff_gate, discrimination_gate, corpus_completeness_gate

ok = True
def check(label, got, want):
    global ok
    p = got == want
    ok = ok and p
    print(f"  [{'PASS' if p else 'FAIL'}] {label}: got={got} want={want}")

print("PRODUCER baseline_cliff_self_check (deterministic is_working_baseline_cliff):")
# B-delta v2 uniform-bipolar: lin 1.0 @low-M -> 0.039 @high-M = WORKING baseline WITH a cliff
check("working+cliff (B-delta v2 bipolar 1.0->0.039)",
      baseline_cliff_self_check(1.0, 0.039)["is_working_baseline_cliff"], True)
# B-delta v2 continuous: 1.0 -> 0.0 = working + cliff
check("working+cliff (B-delta v2 continuous 1.0->0.0)",
      baseline_cliff_self_check(1.0, 0.0)["is_working_baseline_cliff"], True)
# B-delta v1 NOISE-BUG: linear=0 at ALL M = FLOORED everywhere -> NOT a working baseline (the catch)
check("floored everywhere (B-delta v1 0.0->0.0) -> NOT lever",
      baseline_cliff_self_check(0.0, 0.0)["is_working_baseline_cliff"], False)
check("  ...works flag False (floored)",
      baseline_cliff_self_check(0.0, 0.0)["works"], False)
# works EVERYWHERE, no cliff (1.0 -> 0.95, drop 0.05 < 0.2) -> no headroom for a lever
check("no-cliff (1.0->0.95, drop<0.2) -> NOT lever",
      baseline_cliff_self_check(1.0, 0.95)["is_working_baseline_cliff"], False)
check("  ...cliffs flag False (no degradation)",
      baseline_cliff_self_check(1.0, 0.95)["cliffs"], False)
# boundary: drop exactly cliff_drop (0.2) at a working low -> cliffs True
check("boundary drop==cliff_drop (0.8->0.6) -> lever",
      baseline_cliff_self_check(0.8, 0.6)["is_working_baseline_cliff"], True)
# boundary: low exactly works_threshold (0.5) -> works is strict '>' so 0.5 is NOT working
check("boundary low==works_threshold (0.5->0.2) -> NOT working (strict >)",
      baseline_cliff_self_check(0.5, 0.2)["is_working_baseline_cliff"], False)
# bad inputs (None) -> False, no crash
check("bad inputs (None) -> False no-crash",
      baseline_cliff_self_check(None, None)["is_working_baseline_cliff"], False)

print("CONSUMER baseline_cliff_gate (additive + non-retroactive):")
# field present, is_working_baseline_cliff False -> force NON_TEST (the B-delta v1 catch as a gate)
check("floored-baseline PASS -> forced NON_TEST",
      baseline_cliff_gate({"baseline_cliff_self_check": {"is_working_baseline_cliff": False}}, "PASS"),
      "NON_TEST")
# field present, is_working_baseline_cliff True -> verdict UNCHANGED (real lever PASS stays PASS)
check("working-baseline-cliff PASS -> PASS unchanged",
      baseline_cliff_gate({"baseline_cliff_self_check": {"is_working_baseline_cliff": True}}, "PASS"),
      "PASS")
# NON-RETROACTIVE: no field -> verdict UNCHANGED (legacy cert atom preserved, no mass re-grade)
check("legacy cell (no field) PASS -> PASS unchanged (non-retroactive)",
      baseline_cliff_gate({}, "PASS"), "PASS")
check("legacy cell (no field) HARD_FAIL -> unchanged",
      baseline_cliff_gate({"verdict": "x"}, "HARD_FAIL"), "HARD_FAIL")
# malformed field (not a dict) -> unchanged (defensive, legacy-safe)
check("malformed field (str) -> unchanged",
      baseline_cliff_gate({"baseline_cliff_self_check": "oops"}, "PASS"), "PASS")

print("COMPOSITION with discrimination_gate (both can force NON_TEST; order-independent):")
# discrimination False -> NON_TEST, then baseline-cliff (no field) leaves it
m = {"discrimination_self_check": {"discriminates": False}}
v = discrimination_gate(m, "PASS"); v = baseline_cliff_gate(m, v)
check("non-discriminating PASS -> NON_TEST (disc gate)", v, "NON_TEST")
# discrimination True, baseline floored -> baseline-cliff forces NON_TEST
m = {"discrimination_self_check": {"discriminates": True},
     "baseline_cliff_self_check": {"is_working_baseline_cliff": False}}
v = discrimination_gate(m, "PASS"); v = baseline_cliff_gate(m, v)
check("discriminating but floored-baseline PASS -> NON_TEST (cliff gate)", v, "NON_TEST")
# both clean -> PASS survives both gates
m = {"discrimination_self_check": {"discriminates": True},
     "baseline_cliff_self_check": {"is_working_baseline_cliff": True}}
v = discrimination_gate(m, "PASS"); v = baseline_cliff_gate(m, v)
check("both-clean PASS -> PASS survives both gates", v, "PASS")

print("NESTED per-task schema (the multi-task lever cell, e.g. B-delta v2 bipolar+continuous):")
# B-delta v2 ACTUAL schema: discrimination_self_check nested per-task, both discriminate=True -> PASS survives
bdv2_disc = {"discrimination_self_check": {"bipolar": {"discriminates": True},
                                           "continuous": {"discriminates": True}}}
check("nested disc both-True PASS -> PASS (B-delta v2 actual)",
      discrimination_gate(bdv2_disc, "PASS"), "PASS")
# nested with ONE task degenerate -> NON_TEST (the coverage gap the flat gate silently missed)
check("nested disc one-False PASS -> NON_TEST (multi-task coverage)",
      discrimination_gate({"discrimination_self_check": {"a": {"discriminates": True},
                                                         "b": {"discriminates": False}}}, "PASS"), "NON_TEST")
# nested baseline-cliff both working -> PASS; one floored -> NON_TEST
check("nested cliff both-working PASS -> PASS",
      baseline_cliff_gate({"baseline_cliff_self_check": {"a": {"is_working_baseline_cliff": True},
                                                         "b": {"is_working_baseline_cliff": True}}}, "PASS"), "PASS")
check("nested cliff one-floored PASS -> NON_TEST",
      baseline_cliff_gate({"baseline_cliff_self_check": {"a": {"is_working_baseline_cliff": True},
                                                         "b": {"is_working_baseline_cliff": False}}}, "PASS"),
      "NON_TEST")

print("4th gate: CORPUS-COMPLETENESS (absence/coverage must verify FULL corpus -- A2 catch):")
# full corpus, exhaustive method -> complete
check("full+exhaustive (41324/41324, per_topic) -> complete",
      corpus_completeness_self_check("absence", 41324, 41324, "exhaustive_per_topic")["is_complete"], True)
# subset / local-only (the half-data catch: 1935 of 3684) -> incomplete
check("half-data (1935/3684) -> incomplete",
      corpus_completeness_self_check("coverage", 1935, 3684, "local_only")["is_complete"], False)
# full count but ESTIMATE method (the A2 token-match over-flag) -> incomplete (method not exhaustive)
check("full-count but grep-estimate method -> incomplete (A2 over-flag)",
      corpus_completeness_self_check("gap_set", 41324, 41324, "token_match_grep")["is_complete"], False)
# n_total=0 (no corpus) -> incomplete (guard)
check("n_total=0 -> incomplete",
      corpus_completeness_self_check("absence", 0, 0, "exhaustive")["is_complete"], False)
# bad inputs -> incomplete no-crash
check("bad inputs (None) -> incomplete no-crash",
      corpus_completeness_self_check("absence", None, None, "exhaustive")["is_complete"], False)
# CONSUMER: incomplete -> NON_TEST; complete -> unchanged; absent field -> unchanged (non-retroactive)
check("incomplete-corpus PASS -> NON_TEST",
      corpus_completeness_gate({"corpus_completeness_self_check": {"is_complete": False}}, "PASS"), "NON_TEST")
check("complete-corpus PASS -> PASS unchanged",
      corpus_completeness_gate({"corpus_completeness_self_check": {"is_complete": True}}, "PASS"), "PASS")
check("legacy (no field) PASS -> PASS unchanged (non-retroactive)",
      corpus_completeness_gate({}, "PASS"), "PASS")
# nested per-claim: one incomplete -> NON_TEST
check("nested one-incomplete PASS -> NON_TEST",
      corpus_completeness_gate({"corpus_completeness_self_check": {"a": {"is_complete": True},
                                                                  "b": {"is_complete": False}}}, "PASS"), "NON_TEST")
# all 4 gates compose: clean everything -> PASS survives
m = {"discrimination_self_check": {"discriminates": True},
     "baseline_cliff_self_check": {"is_working_baseline_cliff": True},
     "corpus_completeness_self_check": {"is_complete": True}}
v = discrimination_gate(m, "PASS"); v = baseline_cliff_gate(m, v); v = corpus_completeness_gate(m, v)
check("all-4-gates-clean PASS -> PASS survives", v, "PASS")

print(("ALL PASS" if ok else "SOME FAILED"))
sys.exit(0 if ok else 1)
