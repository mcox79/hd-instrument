"""Witness: the perceptual-access observation ledger driven by the IN-SUBSTRATE UD parse (NO spaCy)
does not regress the belief/ToM dimension vs the promoted spaCy-parse PAL, on MODERN false-belief gold.

Population: experiments/data/gold_false_belief_realtext_v1.jsonl (+ v1b) -- 26 modern-English
Sally-Anne passages (19c banned). The observation cue is the discriminator: on false-belief items the
protagonist did NOT witness the move (absence / motion / asleep cues -> the spaCy-dependency cues), on
true-belief items they did (watched / informed). belief-correct on an item <=> observed-bit correct.

Arms (identical inputs; only the observation SOURCE changes):
  PAL_SPACY   the promoted hdlab.perceptual_access_ledger (spaCy parse)               -- current baseline
  PAL_INSUB   experiments._perceptual_access_ledger_insubstrate (pos_tagger+arc_parser+arc_labeler)
  NO_TOM      observed:=True always (shared-reality floor: right on TB, wrong on FB)
  ALWAYS_INIT believed:=initial always (trivial floor: right on FB, wrong on TB)
  TWIN        observed:=random (info-free null)

Run: .venv/Scripts/python.exe verification/test_perceptual_access_ledger_insubstrate.py
"""
from __future__ import annotations

import importlib.util
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def _load_exp():
    path = os.path.join(REPO, "experiments", "exp_theory_of_mind_realtext_v1.py")
    spec = importlib.util.spec_from_file_location("exp_theory_of_mind_realtext_v1", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_PRON = ["he", "she", "they", "him", "her", "them", "his", "hers", "their"]


def _aliases(prot: str):
    return [prot] + _PRON


def _gold_obs(row) -> bool:
    return bool(row["protagonist_saw_move"]) or row["condition"] == "true_belief_informed"


def _belief_qs(row):
    return [q for q in row["questions"] if q["type"] in ("belief", "belief_protagonist")]


def build_items():
    from hdlab.perceptual_access_ledger import PerceptualAccessLedger
    from experiments._perceptual_access_ledger_insubstrate import (
        InSubstratePerceptualAccessLedger, split_sentences)
    exp = _load_exp()
    rows = [r for r in exp.load_gold() if _belief_qs(r)]

    led_spacy = PerceptualAccessLedger()             # spaCy lazy-loaded on first observed()
    led_insub = InSubstratePerceptualAccessLedger()  # in-substrate frontend lazy-loaded

    seg_aligned = 0
    items = []
    for r in rows:
        text = r["text"]
        aliases = _aliases(r["protagonist"])
        obj = r["object"]
        fin = r["final_location"]
        sents_tok = split_sentences(text)
        # locate the move sentence ONCE on the in-substrate parse; pass the SAME event_index to both arms.
        parsed = [led_insub._parse_sent(t) for t in sents_tok if t]
        ev = led_insub._find_event_index(parsed, obj, (), aliases, event_location=fin)

        tr_i = led_insub.observed_over_sents(sents_tok, aliases, event_object=obj,
                                             event_index=ev, event_location=fin)
        # spaCy arm re-segments internally; verify segment counts match so `ev` means the same sentence.
        nlp = led_spacy._nlp_or_load()
        n_spacy = len(list(nlp(text).sents))
        aligned = (n_spacy == len(parsed))
        seg_aligned += int(aligned)
        tr_s = led_spacy.observed(text, aliases, event_object=obj,
                                  event_index=ev, event_location=fin)

        items.append(dict(row=r, gold_obs=_gold_obs(r), obs_spacy=bool(tr_s.observed),
                          obs_insub=bool(tr_i.observed), tr_spacy=tr_s, tr_insub=tr_i,
                          aligned=aligned, n_sents=len(parsed), ev=ev))
    return exp, rows, items, seg_aligned


def _belief_acc(items, arm, rng=None):
    """belief accuracy over all protagonist belief questions for one arm."""
    from experiments.exp_theory_of_mind_realtext_v1 import believed_location
    vals = []
    for it in items:
        r = it["row"]
        init, fin = r["initial_location"], r["final_location"]
        if arm == "PAL_SPACY":
            obs = it["obs_spacy"]
        elif arm == "PAL_INSUB":
            obs = it["obs_insub"]
        elif arm == "NO_TOM":
            obs = True
        elif arm == "TWIN":
            obs = bool(rng.integers(0, 2))
        else:
            obs = None
        for q in _belief_qs(r):
            if arm == "ALWAYS_INIT":
                pred = init
            else:
                pred = believed_location(obs, init, fin)
            vals.append(int(pred == q["gold"]))
    return vals


def _obs_acc(items, key):
    return [int(it[key] == it["gold_obs"]) for it in items]


def main():
    exp, rows, items, seg_aligned = build_items()
    n = len(items)
    fb = [it for it in items if it["row"]["condition"].startswith("false_belief")]
    tb = [it for it in items if not it["row"]["condition"].startswith("false_belief")]

    # ---- observation-cue accuracy (the load-bearing bit) ----
    oa_s = _obs_acc(items, "obs_spacy")
    oa_i = _obs_acc(items, "obs_insub")
    agree = np.mean([int(it["obs_spacy"] == it["obs_insub"]) for it in items])

    # ---- belief accuracy per arm + bootstrap CI ----
    def ci(vals):
        return exp.boot_ci(vals, seed=20260908)

    b_s = _belief_acc(items, "PAL_SPACY")
    b_i = _belief_acc(items, "PAL_INSUB")
    b_no = _belief_acc(items, "NO_TOM")
    b_ai = _belief_acc(items, "ALWAYS_INIT")

    sm, slo, shi, shw = ci(b_s)
    im, ilo, ihi, ihw = ci(b_i)
    nom, nlo, nhi, _ = ci(b_no)
    aim, alo, ahi, _ = ci(b_ai)

    # ---- info-free TWIN null: p95 of belief_acc under random observation ----
    null_accs = []
    for s in range(400):
        rng = np.random.default_rng(1000 + s)
        null_accs.append(float(np.mean(_belief_acc(items, "TWIN", rng))))
    null_p95 = float(np.percentile(null_accs, 95))
    null_mean = float(np.mean(null_accs))

    print(f"=== PAL in-substrate vs spaCy | modern false-belief gold ===")
    print(f"n_passages={n}  (false_belief={len(fb)} true_belief={len(tb)})  "
          f"belief_Qs={len(b_s)}  seg_aligned={seg_aligned}/{n}")
    print(f"observation-cue acc:  spaCy={np.mean(oa_s):.3f}  in-substrate={np.mean(oa_i):.3f}  "
          f"agreement={agree:.3f}")
    print(f"belief acc [95% CI]:")
    print(f"  PAL_SPACY    {sm:.3f} [{slo:.3f},{shi:.3f}]  (hw {shw:.3f})")
    print(f"  PAL_INSUB    {im:.3f} [{ilo:.3f},{ihi:.3f}]  (hw {ihw:.3f})")
    print(f"  NO_TOM floor {nom:.3f} [{nlo:.3f},{nhi:.3f}]")
    print(f"  ALWAYS_INIT  {aim:.3f} [{alo:.3f},{ahi:.3f}]")
    print(f"  TWIN null    mean={null_mean:.3f}  p95={null_p95:.3f}")

    # ---- per-item disagreements (the diagnostic for where the in-substrate parse differs) ----
    diffs = [it for it in items if it["obs_spacy"] != it["obs_insub"]]
    print(f"\nDISAGREEMENTS spaCy vs in-substrate: {len(diffs)}")
    for it in diffs:
        r = it["row"]
        print(f"  [{r['passage_id']}] gold_obs={it['gold_obs']} spaCy={it['obs_spacy']} "
              f"insub={it['obs_insub']} aligned={it['aligned']}")
        print(f"    spaCy:  {it['tr_spacy'].reason}")
        print(f"    insub:  {it['tr_insub'].reason}")

    # ---- items each arm gets WRONG (vs gold) ----
    wrong_s = [it['row']['passage_id'] for it in items if it['obs_spacy'] != it['gold_obs']]
    wrong_i = [it['row']['passage_id'] for it in items if it['obs_insub'] != it['gold_obs']]
    print(f"\nspaCy wrong on gold ({len(wrong_s)}): {wrong_s}")
    print(f"insub wrong on gold ({len(wrong_i)}): {wrong_i}")

    # ---- gates (each can fail) ----
    gate_no_regress = ilo >= slo - 0.05 or ilo > nhi   # CI-overlap no-regress OR beats floor CI-sep
    gate_beats_null = im > null_p95
    gate_beats_floors = (ilo > nhi) and (ilo > ahi)
    print("\nGATES:")
    print(f"  {'PASS' if gate_no_regress else 'fail'}  in-substrate no-regress vs spaCy "
          f"(insub_lo {ilo:.3f} >= spacy_lo {slo:.3f} - 0.05, or beats NO_TOM CI)")
    print(f"  {'PASS' if gate_beats_null else 'fail'}  in-substrate beats info-free null p95 "
          f"({im:.3f} > {null_p95:.3f})")
    print(f"  {'PASS' if gate_beats_floors else 'fail'}  in-substrate beats BOTH floors CI-separated "
          f"(insub_lo {ilo:.3f} > NO_TOM_hi {nhi:.3f} and ALWAYS_INIT_hi {ahi:.3f})")

    assert gate_beats_null, "in-substrate PAL must beat the info-free null p95"
    assert gate_no_regress, "in-substrate PAL must not regress the belief dim vs spaCy"
    print("\nWITNESS PASSED")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
