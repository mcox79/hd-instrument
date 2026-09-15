"""Scaffold-free witness for the register-native selectional/event store (slug
the_selectional_event_store_is_learned_from_the_wrong_domain_needs_a_register_native_corpus).

Proves the HEADLINE on the held-out QA-SRL science test, rebuilding the stores from the DISJOINT
domain corpora (no gold, no test sentences -- leakage-guarded at parse time):

  W1  PASS -- the FHRR-bound register-native (science) event store RECOVERS who-did-what CI-separated
      over the out-of-domain (simplewiki) FHRR store (the brain-foundational codec carries the domain).
  W2  control -- the VERB-SHUFFLED twin (same science triples, verb keys permuted) LOSES CI-separated
      (the verb-KEYING does the work, not any per-candidate scorer).
  W3  control -- the WRONG-DOMAIN (fiction) marginal store does NOT beat simplewiki; the science store
      BEATS fiction CI-separated (the DOMAIN, not any disjoint corpus, does the work).
  W4  LOCATED CORRECTION -- the MARGINAL (verb->OBJ) science store does NOT CI-beat simplewiki (the
      parent's +0.149 was topical near-leakage from leave-one-sentence-out on the TEST corpus; the true
      deployable disjoint-domain effect lives in the JOINT event structure, not the marginal preference).

Reuses the landed pair caches under data/exp_register_native_store_v1/ (built by
experiments/exp_register_native_store_v1.py --parse ...). NO external LLM. ASCII. Read-only.
"""
from __future__ import annotations
import os, sys, json
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import torch
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_register_native_store_v1 as E
import experiments.exp_fhrr_event_role_assignment_v1 as F
from hdlab.situation_model_accumulate import unit_phase_vec

OUT = os.path.join(_REPO, "data/exp_register_native_store_v1")
TOK = int(os.environ.get("RNS_TOK", "1200000"))   # which token-budget caches to witness
NBOOT = 1000


def _cache(name):
    p = os.path.join(OUT, "pairs_%s_%dtok.json" % (name, TOK))
    if not os.path.exists(p):
        raise SystemExit("MISSING CACHE %s -- run: exp_register_native_store_v1.py --parse %s --tokens %d"
                         % (p, name, TOK))
    return json.load(open(p))


def main():
    parsed = {n: _cache(n) for n in ("science", "simplewiki", "fiction")}
    for n, d in parsed.items():
        assert d["n_leak"] == 0, "LEAKAGE: %s store contains %d test sentences" % (n, d["n_leak"])

    vocab = set()
    for d in parsed.values():
        for v, o in d["verb_obj"]:
            vocab.add(o)
        for s, v, o in d["svo"]:
            vocab.add(s); vocab.add(o)
    rows = V1.load_pop(V1.QA)
    for r in rows:
        vocab.update(h for h in r["cand_heads"] if len(h) >= 3)
        vocab.add(r["gold_head"])
    gv = E.load_glove_union(vocab)

    marg = {n: E.build_marginal(parsed[n], gv) for n in parsed}
    marg_shuf = E.verbshuffle(marg["science"])
    enc = F.make_encoder()
    A = unit_phase_vec(E.D, torch.Generator().manual_seed(1)).to(torch.complex64)
    P = unit_phase_vec(E.D, torch.Generator().manual_seed(2)).to(torch.complex64)
    fhrr = {n: E.build_fhrr(parsed[n], gv, enc, A, P) for n in ("science", "simplewiki")}
    fhrr_shuf = E.verbshuffle(fhrr["science"])

    cands = E.make_cands(gv)
    m_sci = E.marginal_pick_fn(marg["science"], cands)
    m_sw = E.marginal_pick_fn(marg["simplewiki"], cands)
    m_fic = E.marginal_pick_fn(marg["fiction"], cands)
    m_shuf = E.marginal_pick_fn(marg_shuf, cands)
    f_sci = E.fhrr_pick_fn(fhrr["science"], cands, enc, A, P)
    f_sw = E.fhrr_pick_fn(fhrr["simplewiki"], cands, enc, A, P)
    f_shuf = E.fhrr_pick_fn(fhrr_shuf, cands, enc, A, P)

    # pooled ambiguous slice: (passive OR noncanonical) AND non-reversible
    pool = [r for r in rows if (r.get("voice") == "passive" or r.get("noncanonical"))
            and len(cands(r)) >= 2 and sum(1 for h, _, _ in cands(r) if E.anim(h)) < 2]
    mrows = [r for r in pool if V1._lem(r["verb"]) in marg["science"] and V1._lem(r["verb"]) in marg["simplewiki"]]
    frows = [r for r in pool if V1._lem(r["verb"]) in fhrr["science"] and V1._lem(r["verb"]) in fhrr["simplewiki"]]

    def dlt(rowset, a, b):
        return V1.paired_delta(rowset, a, b, NBOOT)

    out = {}
    # W1 -- FHRR recovery (the PASS)
    d = dlt(frows, f_sci, f_sw); out["W1_FHRR_science_vs_simplewiki"] = d
    assert d["delta"] > 0 and d["frac_le_0"] < 0.05, \
        "W1 FAIL: FHRR science must CI-beat simplewiki, got d=%+.4f frac<=0=%.3f" % (d["delta"], d["frac_le_0"])
    # W2 -- verb-shuffled twin loses
    d = dlt(frows, f_sci, f_shuf); out["W2_FHRR_science_vs_verbshuf"] = d
    assert d["delta"] > 0 and d["frac_le_0"] < 0.05, \
        "W2 FAIL: FHRR science must CI-beat its verb-shuffled twin, got d=%+.4f frac<=0=%.3f" % (d["delta"], d["frac_le_0"])
    # W3 -- domain beats wrong-domain (fiction); fiction does not beat simplewiki
    d = dlt(mrows, m_sci, m_fic); out["W3a_marg_science_vs_fiction"] = d
    assert d["delta"] > 0 and d["frac_le_0"] < 0.05, \
        "W3a FAIL: science must CI-beat fiction, got d=%+.4f frac<=0=%.3f" % (d["delta"], d["frac_le_0"])
    d = dlt(mrows, m_fic, m_sw); out["W3b_marg_fiction_vs_simplewiki"] = d
    assert d["delta"] < 0, "W3b FAIL: fiction must NOT beat simplewiki, got d=%+.4f" % d["delta"]
    # W4 -- located correction: marginal science does NOT CI-beat simplewiki
    d = dlt(mrows, m_sci, m_sw); out["W4_marg_science_vs_simplewiki_TIE"] = d
    assert d["frac_le_0"] > 0.05, \
        "W4 FAIL: marginal science was expected to TIE simplewiki (parent +0.149 was leakage), got frac<=0=%.3f" % d["frac_le_0"]
    # also: marginal verb-keying still works (twin loses)
    d = dlt(mrows, m_sci, m_shuf); out["W5_marg_science_vs_verbshuf"] = d
    assert d["delta"] > 0 and d["frac_le_0"] < 0.05, \
        "W5 FAIL: marginal science must CI-beat its twin, got d=%+.4f frac<=0=%.3f" % (d["delta"], d["frac_le_0"])

    print(json.dumps({"tokens": TOK, "n_fhrr": len(frows), "n_marg": len(mrows),
                      "results": {k: {"delta": v["delta"], "ci_lo": v["ci_lo"], "ci_hi": v["ci_hi"],
                                      "frac_le_0": v["frac_le_0"]} for k, v in out.items()}}, indent=2))
    print("ALL WITNESSES PASSED (5/5 + 2 sub-checks)")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
