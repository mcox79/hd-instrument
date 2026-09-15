"""Scaffold-free witness for wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector.

Runs a small standalone SemCor evaluation through the organ and asserts the located-negative's load-bearing
claims (each is a can-fail check, not a tautology):
  W1  unit self-test (AUC / score / conflict / suppression invariants) passes.
  W2  DIRECTIONAL predictive-error detector (domI = N400 on the dominant reading) is REAL and BEATS the
      symmetric-conflict and bag detectors -- struct_domI > struct_sym > bag_sym, and struct_domI > 0.60.
      (Contradicts the brief's 'detectors cap at ~0.51'; the brain-faithful directional signal is better.)
  W3  the frequency-independent structural signal produces a REAL subordinate recovery (best gated config
      lifts the subordinate population > +0.05 over the MFS floor).
  W4  the SEE-SAW WALL: NO gated config beats the MFS floor CI-separated on the FULL population (the located
      negative), AND the info-free shuffled-structure twin does not beat the real full-population net.

Standalone (parses 2 SemCor files with spaCy locally, ~3-5 min; no scratchpad dependency). Deterministic.
"""
import os
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_topdown_situation_sense_selector_v1 as C


def main():
    checks = []

    # W1 -- unit invariants
    try:
        C.self_test()
        checks.append(("W1 self-test (unit invariants)", True, "unit checks pass"))
    except Exception as e:  # noqa
        checks.append(("W1 self-test (unit invariants)", False, "raised %r" % e))
        _report(checks); return 1

    # small standalone end-to-end run (2 SemCor files)
    out = C.run("smoke", max_files=2, quantile=0.80, gamma=3.0, lam=1.0)
    auc = out["detector_auc"]
    c = out["contrasts"]

    # W2 -- directional detector real + best
    w2 = (auc["struct_domI"] > auc["struct_sym"] > auc["bag_sym"]) and auc["struct_domI"] > 0.60
    checks.append(("W2 directional detector real+best (struct_domI>struct_sym>bag_sym, >0.60)", bool(w2),
                   "struct_domI=%.3f struct_sym=%.3f bag_sym=%.3f" %
                   (auc["struct_domI"], auc["struct_sym"], auc["bag_sym"])))

    # W3 -- a real subordinate recovery EXISTS at some operating point (aggressive firing), i.e. the
    # structural/directional signal genuinely recovers rare senses (the see-saw is a NET problem, not a
    # no-signal problem). Scan the sweep for the max subordinate recovery.
    max_sub = max((r.get("net_sub", -1.0) for rows in out["sweep"].values()
                   for r in rows if isinstance(r, dict)), default=-1.0)
    w3 = max_sub > 0.05
    checks.append(("W3 subordinate recovery EXISTS in sweep (max net_sub > +0.05)", bool(w3),
                   "max net_sub=%+.4f" % max_sub))

    # W4 -- the see-saw wall (located negative): the NET-best config does NOT beat MFS on the full
    # population (CI includes 0 or below), AND the info-free twin does not beat the real full-pop net.
    full_beats = c["best_vs_prior_NET_full"]["beats"]
    twin_net = out["best_struct_shuf_net"]
    real_full_net = out["best_combo_gated"]["net_full"]
    w4 = (full_beats is False) and (twin_net <= real_full_net + 1e-9)
    checks.append(("W4 see-saw wall: no full-pop CI-separated gain AND twin<=real", bool(w4),
                   "full_beats_prior=%s twin_net=%+.4f real_full_net=%+.4f" %
                   (full_beats, twin_net, real_full_net)))

    return _report(checks)


def _report(checks):
    npass = sum(1 for _, ok, _ in checks if ok)
    print("\n==== WITNESS: %d/%d ====" % (npass, len(checks)))
    for name, ok, detail in checks:
        print("  [%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
    return 0 if npass == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
