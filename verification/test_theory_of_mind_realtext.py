"""Scaffold-free witness for false-belief (Theory of Mind) on real text, on the substrate's own organs.

Reproduces the headline WITHOUT re-running/overwriting the landed cell. Each test can fail.
  (A) the per-agent FHRR belief partition (hdlab.binding) solves false belief and a shared-reality
      store does NOT -- on a tiny hand fixture (no gold file needed);
  (B) on the real-text gold, FULL_TOM beats the shared-reality floor, the trivial always-initial floor,
      and the info-free (scrambled-observation) twin, all CI-separated, while keeping reality intact.

Run: .venv/Scripts/python.exe verification/test_theory_of_mind_realtext.py
"""
from __future__ import annotations

import importlib.util
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def _load_exp():
    path = os.path.join(REPO, "experiments", "exp_theory_of_mind_realtext_v1.py")
    spec = importlib.util.spec_from_file_location("exp_theory_of_mind_realtext_v1", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_belief_partition_on_substrate_organs():
    """A per-agent FHRR bank that keeps the OLD binding for a non-observer recovers the FALSE belief;
    a shared-reality bank recovers the TRUE location (and so fails the false-belief question)."""
    from hdlab import binding
    from hdlab.situation_model_accumulate import unit_phase_vec, cleanup_argmax
    import torch
    g = torch.Generator(); g.manual_seed(7)
    d = 512
    obj = unit_phase_vec(d, g)
    red, blue = unit_phase_vec(d, g), unit_phase_vec(d, g)
    vocab = {"red": red, "blue": blue}
    # Anna put it in red, did NOT see it moved to blue.
    world_bank = binding.bind(obj, blue)                     # truth
    anna_bank = binding.bind(obj, red)                       # stale = false belief
    anna_belief, _ = cleanup_argmax(binding.unbind(anna_bank, obj), vocab)
    reality, _ = cleanup_argmax(binding.unbind(world_bank, obj), vocab)
    shared, _ = cleanup_argmax(binding.unbind(world_bank, obj), vocab)  # NO_TOM answers belief from world
    assert anna_belief == "red", f"per-agent bank must recover the false belief (red): {anna_belief}"
    assert reality == "blue", f"world bank must recover reality (blue): {reality}"
    assert shared == "blue", "shared-reality (NO_TOM) answers the belief question WRONG (blue) -- the deficit"
    print("PASS belief_partition_on_substrate_organs (false belief=red, reality=blue, NO_TOM=blue=wrong)")


def test_realtext_full_tom_beats_floors_and_twin():
    exp = _load_exp()
    rows = exp.load_gold()
    assert len(rows) >= 20, f"need the expanded gold for power: {len(rows)}"
    codes = exp.Codes(20260826)
    loc_strings = sorted({r[k] for r in rows for k in ("initial_location", "final_location")})
    loc_vocab = {s: codes.get("loc", s) for s in loc_strings}
    import numpy as np

    def belief_acc(arm):
        rng = np.random.default_rng((hash(arm) ^ 20260826) & 0x7FFFFFFF)
        vals = []
        for r in rows:
            ans = ({q["type"]: r["initial_location"] for q in r["questions"]}
                   if arm == "ALWAYS_INITIAL" else exp.build_answer(arm, r, codes, rng, loc_vocab))
            for q in r["questions"]:
                if q["type"].startswith("belief"):
                    vals.append(int(ans[q["type"]] == q["gold"]))
        return vals

    ft = belief_acc("FULL_TOM")
    fb_ft = [v for r in rows for q in r["questions"] if q["type"].startswith("belief") and r["condition"].startswith("false_belief") for v in [int(exp.build_answer("FULL_TOM", r, codes, np.random.default_rng(1), loc_vocab)[q["type"]] == q["gold"])]]
    no = belief_acc("NO_TOM")
    ai = belief_acc("ALWAYS_INITIAL")
    tw = belief_acc("TWIN")

    def ci(vals):
        return exp.boot_ci(vals, seed=20260826 + 1)

    ftm, ftlo, fthi, _ = ci(ft)
    nom, nolo, nohi, _ = ci(no)
    aim, ailo, aihi, _ = ci(ai)
    twm, twlo, twhi, _ = ci(tw)
    assert ftlo > nohi, f"FULL_TOM ({ftm:.3f}) must beat shared-reality floor ({nom:.3f}) CI-separated"
    assert ftlo > aihi, f"FULL_TOM ({ftm:.3f}) must beat always-initial floor ({aim:.3f}) CI-separated"
    assert ftlo > twhi, f"FULL_TOM ({ftm:.3f}) must beat the info-free twin ({twm:.3f}) CI-separated"
    assert sum(fb_ft) == len(fb_ft), "FULL_TOM must solve every false-belief question"
    print(f"PASS realtext_full_tom (FULL_TOM {ftm:.3f}[{ftlo:.3f},{fthi:.3f}] > NO_TOM {nom:.3f}, "
          f"ALWAYS_INITIAL {aim:.3f}, TWIN {twm:.3f}; false-belief solved {sum(fb_ft)}/{len(fb_ft)})")


def main():
    tests = [test_belief_partition_on_substrate_organs,
             test_realtext_full_tom_beats_floors_and_twin]
    for t in tests:
        t()
    print(f"\nALL {len(tests)} WITNESS TESTS PASSED")


if __name__ == "__main__":
    main()
