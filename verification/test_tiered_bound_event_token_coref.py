"""Scaffold-free witness for `the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token`.

Recomputes the load-bearing claims FROM SOURCE on REAL passages (no landed metrics.json read, no replay):
the assembled TIERED bound-event-token backbone stores the JOINT the parallel silos cannot. Every check
can fail.

  [1] MECHANISM (real LitBank old fiction): JOINT bound-token coref beats the LATE-FUSION-OF-MARGINALS
      silo CI-separated, and beats the LEXICAL/surface floor CI-separated.
  [2] BINDING-SHUFFLE control LOSES: permuting within-event bindings (marginals identical, joint destroyed)
      collapses the joint arm to <= marginal level (CI-separated below the intact joint).
  [3] INFO-FREE TWIN null: random tokens do not beat marginal (the joint win is not a decode artifact).
  [4] MUST CHUNK: a single FLAT bundle collapses at passage scale (M up) while the MULTIBANK slotted and
      DG+CA3 tiered registers do NOT (they stay >= the flat arm, CI/margin by construction).
  [5] SYMBOLIC CEILING is ~1.0 and the JOINT approaches it while the MARGINAL silo does not (the joint is
      the neurally-realizable route to the symbolic target; the silo cannot get there).
  [6] GENERALIZES: the JOINT > MARGINAL mechanism holds on MODERN UD-EWT web text too (not a corpus-age
      artifact of old fiction).
  [7] HARD-NEG localisation: the joint's entire advantage is on the RECOMBINATION hard negatives (the joint
      test), and the marginal silo is at/below chance there -- the non-gameable discriminator.

Brain frame (PINNED): ONE bound event token per event indexed on all dimensions (Zwaan & Radvansky 1998;
Franklin 2020 SEM); recognising same-event = CA3 pattern completion (Marr 1971); the recombination /
binding-shuffle control is the conjunctive-memory dissociation (Konkel & Cohen 2009). Glass-box, NO LLM.

Run: .venv/Scripts/python.exe verification/test_tiered_bound_event_token_coref.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402
import experiments.exp_tiered_bound_event_token_coref_v1 as E  # noqa: E402


def main():
    SEED = 20260831
    NB = 1500
    # --- real corpora (small witness scale, still real passages) ---
    lit = E.load_litbank_passages(16)
    ud = E.load_udewt_passages(220)
    assert len(lit) >= 8, "need real LitBank passages; got %d" % len(lit)
    assert len(ud) >= 8, "need real UD-EWT passages; got %d" % len(ud)
    rl = E.run_genre(lit, "litbank", SEED, NB)
    ru = E.run_genre(ud, "udewt", SEED + 5000, NB)

    def A(res, arm, subset="all"):
        return res["arms"][arm][subset]

    checks = []

    # [1] MECHANISM on old fiction: joint CI-separated over marginal AND lexical.
    j, mg, lx = A(rl, "joint"), A(rl, "marginal"), A(rl, "lexical")
    checks.append((j["ci_lo"] > mg["ci_hi"],
                   "[1] LitBank JOINT %.3f[%.3f,%.3f] CI-ABOVE MARGINAL %.3f[%.3f,%.3f] (sep=%.3f)"
                   % (j["point"], j["ci_lo"], j["ci_hi"], mg["point"], mg["ci_lo"], mg["ci_hi"],
                      j["ci_lo"] - mg["ci_hi"])))
    checks.append((j["ci_lo"] > lx["ci_hi"],
                   "[1] LitBank JOINT CI-ABOVE LEXICAL %.3f[%.3f,%.3f] (sep=%.3f)"
                   % (lx["point"], lx["ci_lo"], lx["ci_hi"], j["ci_lo"] - lx["ci_hi"])))

    # [2] binding-shuffle LOSES (CI below intact joint).
    sh = A(rl, "joint_shuffle")
    checks.append((sh["ci_hi"] < j["ci_lo"],
                   "[2] BINDING-SHUFFLE %.3f[%.3f,%.3f] CI-BELOW intact JOINT (sep=%.3f) -> joint uses binding"
                   % (sh["point"], sh["ci_lo"], sh["ci_hi"], j["ci_lo"] - sh["ci_hi"])))

    # [3] info-free twin does NOT beat marginal.
    tw = A(rl, "twin")
    checks.append((tw["point"] <= mg["ci_hi"] + 1e-9,
                   "[3] INFO-FREE TWIN %.3f does NOT beat MARGINAL upper %.3f (null holds)"
                   % (tw["point"], mg["ci_hi"])))

    # [4] must chunk: flat collapses; multibank + tiered do not.
    cap = E.capacity_curve(m_values=(8, 32, 128, 256), reps=3)
    flat, mb, tier = cap["flat_single_bundle"], cap["multibank_slotted"], cap["dg_ca3_tiered"]
    checks.append((flat[-1] < flat[0] - 0.1 and mb[-1] >= flat[-1] and tier[-1] >= flat[-1],
                   "[4] MUST CHUNK: flat single-bundle %s COLLAPSES; multibank %s + DG/CA3 tiered %s hold"
                   % (flat, mb, tier)))

    # [5] symbolic ceiling ~1.0; joint approaches it, marginal does not.
    sym = A(rl, "symbolic")
    checks.append((sym["point"] >= 0.98 and (j["point"] - mg["point"]) > 0.0
                   and (sym["point"] - j["point"]) < (sym["point"] - mg["point"]),
                   "[5] SYMBOLIC CEILING %.3f ; JOINT %.3f closer to it than MARGINAL %.3f"
                   % (sym["point"], j["point"], mg["point"])))

    # [6] GENERALIZES to modern web text.
    ju, mu = A(ru, "joint"), A(ru, "marginal")
    checks.append((ju["ci_lo"] > mu["ci_hi"],
                   "[6] MODERN UD-EWT JOINT %.3f[%.3f,%.3f] CI-ABOVE MARGINAL %.3f[%.3f,%.3f] (sep=%.3f)"
                   % (ju["point"], ju["ci_lo"], ju["ci_hi"], mu["point"], mu["ci_lo"], mu["ci_hi"],
                      ju["ci_lo"] - mu["ci_hi"])))

    # [7] hard-neg localisation: joint reject rate high, marginal at/below chance on the recombinations.
    jh, mgh = A(rl, "joint", "hard_neg"), A(rl, "marginal", "hard_neg")
    checks.append((jh["point"] > 0.7 and mgh["point"] < 0.15 and jh["ci_lo"] > mgh["ci_hi"],
                   "[7] HARD-NEG (recombination): JOINT rejects %.3f vs MARGINAL %.3f (silo accepts the join it "
                   "cannot see) -- the non-gameable discriminator" % (jh["point"], mgh["point"])))

    # [8] CUED RETRIEVAL CAPABILITY GAP: the tiered bound token retrieves a specific event from a partial
    # mention (pattern completion); the MARGINAL silo is at chance (1/M) -- a whole capability it LACKS.
    pcc = E.partial_cue_completion(ud[:60], SEED + 900)
    fh0 = pcc["fhrr_direct"]["drop1"]; mg0 = pcc["marginal_silo"]["drop1"]
    checks.append((fh0 is not None and fh0 > 0.9 and mg0 < 0.1,
                   "[8] CUED RETRIEVAL from a partial mention: bound token %.3f vs MARGINAL silo %.3f (chance "
                   "1/M) -- the silo STRUCTURALLY cannot address an event (pattern completion is binding-only)"
                   % (fh0, mg0)))

    # [9] NECESSITY: the grounded (brain-faithful, ATL-hub concept) bound token BEATS the symbolic dict AND
    # arbitrary-symbol binding under PARAPHRASE (verb->WordNet synonym); all tie without paraphrase.
    try:
        import experiments.exp_grounded_binding_paraphrase_coref_v1 as GB
        gd = GB.evaluate(GB.MAIN.load_udewt_passages(300, min_events=6))
        pex, ppar = gd["exact_control"], gd["paraphrase"]
        nec_ok = (pex["grounded"] >= 0.99 and pex["symbol"] >= 0.99             # tie without paraphrase
                  and ppar["grounded"] > ppar["symbol"] + 0.08                   # grounded beats symbol...
                  and ppar["symbol"] <= ppar["chance_uniform"] + 0.02            # ...which is at chance
                  and ppar["grounded_shuffled"] <= ppar["chance_uniform"] + 0.02)  # twin at chance
        checks.append((nec_ok,
                       "[9] NECESSITY (paraphrase coref, n=%d): grounded %.3f BEATS symbol %.3f / symbolic %.3f "
                       "/ shuffled-twin %.3f (chance %.3f); exact-control all tie (%.2f/%.2f) -> grounded binding "
                       "is NECESSARY for graded matching, not just sufficient"
                       % (gd["n_instances"], ppar["grounded"], ppar["symbol"], ppar["symbolic"],
                          ppar["grounded_shuffled"], ppar["chance_uniform"], pex["grounded"], pex["symbol"])))
    except Exception as e:
        checks.append((False, "[9] NECESSITY check errored: %s: %s" % (type(e).__name__, e)))

    print("=== witness: tiered bound-event-token coref (LitBank n=%d, UD-EWT n=%d) ==="
          % (rl["n_passages"], ru["n_passages"]))
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg))
        ok_all = ok_all and bool(ok)
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
