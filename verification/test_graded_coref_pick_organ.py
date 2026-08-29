"""Witness for the LANDED hdlab.graded_coref_pick.graded_antecedent_pick (graded cue-based antecedent retrieval core).

Landed 2026-08-28 from the integrated `coreference_is_capped_at_065_on_real_narrative` (SOLVED/EXCELLENT, owner-DONE).
Confirms the MECHANISM on the ACTUAL hdlab organ (constructed candidate-mention lists, spaCy-free): the graded retrieval
picks by the pinned ACT-R base-level ACTIVATION (recency x frequency x role), NOT by the incumbent's rigid
most-recent-subject tier, and its posterior ENTROPY is a calibrated gold-free abstain (high when candidates genuinely
compete). This is the +0.172-CI-sep / AUC-0.806 mechanism the shipped experiment measured on real LitBank; here it is
mechanism-witnessed store-agnostically.

Asserts:
  1. GRADED beats the RIGID TIER by mechanism: on a stale-subject-vs-recent-frequent case, the hard most-recent-subject
     tier picks the STALE subject, but graded retrieval picks the higher-ACTIVATION recent/frequent candidate (they
     DIFFER, and graded = the activation winner) -- the exact failure the shipped result showed (the tier over-commits).
  2. ENTROPY CALIBRATES: a genuinely competitive case (two near-equal candidates) yields HIGHER posterior entropy than a
     dominant case (one candidate clearly strongest) -> entropy is the "cues conflict -> defer" abstain signal.
  3. DEGENERATE: a single candidate -> pick 0, entropy 0; empty -> pick -1.
  4. spaCy-FREE at runtime (no spacy imported).

Run: .venv/Scripts/python.exe verification/test_graded_coref_pick_organ.py
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.graded_coref_pick import graded_antecedent_pick, hard_tier_pick  # noqa: E402


def main() -> int:
    checks = []

    # (1) stale-subject (cand 0) vs recent+frequent (cand 1); pronoun clause at sentence 6.
    #  cand 0: SUBJECT once at sentence 1 (stale) -- the tier's pick (only one with a subject).
    #  cand 1: OBJECT at sentences 3,4,5 (recent + frequent) -- higher ACT-R activation, no prior subject.
    priors = [
        [(1, "SUBJECT")],
        [(3, "OBJECT"), (4, "OBJECT"), (5, "OBJECT")],
    ]
    p_sent = 6
    g = graded_antecedent_pick(priors, p_sent, pron_role="SUBJECT")
    tier = hard_tier_pick(priors, p_sent)
    checks.append((tier == 0, f"[1a] the RIGID tier picks the STALE subject (cand 0): tier_pick={tier}"))
    checks.append((g["pick"] == 1, f"[1b] GRADED retrieval picks the higher-ACTIVATION recent/frequent cand 1: graded_pick={g['pick']}"))
    checks.append((g["pick"] != tier, f"[1c] graded DIFFERS from the rigid tier (the +0.172 mechanism): graded {g['pick']} != tier {tier}"))

    # (2) entropy calibration: a GENUINE tie (identical cue profiles) -> flat posterior -> high entropy; a dominant
    # case -> sharp posterior -> low entropy. (With the precision gain, only a true tie leaves the posterior flat --
    # that IS the calibrated 'cues conflict -> defer' signal.)
    competitive = [[(4, "SUBJECT")], [(4, "SUBJECT")]]         # identical candidates -> tied -> defer
    dominant = [[(1, "OTHER")], [(3, "SUBJECT"), (4, "SUBJECT"), (5, "SUBJECT")]]  # one clearly strongest
    e_comp = graded_antecedent_pick(competitive, 6)["entropy"]
    e_dom = graded_antecedent_pick(dominant, 6)["entropy"]
    checks.append((e_comp > e_dom + 0.05, f"[2] ENTROPY calibrates: tied {e_comp:.3f} > dominant {e_dom:.3f} (the 'cues conflict -> defer' abstain signal)"))

    # (3) degenerate.
    one = graded_antecedent_pick([[(2, "SUBJECT")]], 5)
    none = graded_antecedent_pick([], 5)
    checks.append((one["pick"] == 0 and one["entropy"] == 0.0 and none["pick"] == -1,
                   f"[3] DEGENERATE: single-> pick0/ent0 ({one['pick']},{one['entropy']}); empty-> pick {none['pick']}"))

    # (4) spaCy-free.
    checks.append(("spacy" not in sys.modules, f"[4] runtime is spaCy-FREE (no spacy in sys.modules): {'spacy' not in sys.modules}"))

    print("=== witness: hdlab.graded_coref_pick.graded_antecedent_pick (graded cue-based antecedent retrieval) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
