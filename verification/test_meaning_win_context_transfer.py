"""Scaffold-free witness for slug the_meaning_win_is_offline_context_free_and_unwired.

HEADLINE (recomputed here first-hand from the fact set + the STATIC grounded norms asset -- no
corpus, no scaffold):
  The offline, context-free grounded meaning win does NOT transfer to context-conditioned sense
  selection. Specifically, on the reused leakage-controlled WSD instrument:
    (1) THE FREQUENCY PRIOR WORKS: most-frequent-sense beats the uniform floor CI-separated -- it is
        the working half of the brain's reordered-access mechanism, and it is currently UNWIRED.
    (2) CONTEXT-CONDITIONED GROUNDED SELECTION IS AT CHANCE ON THE FREQUENCY-DEFEATING ITEMS: on
        subordinate-congruent trials (true sense NOT the most frequent), the grounded context read-out
        (GNOC = the exact rep that won the offline metric) is NOT CI-separated above uniform chance,
        and it TIES its own info-free (shuffled-grounding) twin -- i.e. it carries no real grounded
        signal here, in sharp contrast to the offline base where the twin LOST decisively.
    (3) THE EXPERIENCE PROTOTYPE IS BLIND TO RARE SENSES: it reads DOMINANT senses above chance but
        the subordinate cell is structurally tiny (a sense seen once has no held-out prototype).
  The corpus-dependent distributional/fusion claims (associative channel >= grounded; grounded adds
  nothing when fused) are asserted from the landed metrics.json (re-run the cell to reproduce).

Run: .venv/Scripts/python.exe verification/test_meaning_win_context_transfer.py
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_context_conditioned_sense_selection_v1 import load_multisense_eval
from experiments.exp_context_conditioned_meaning_transfer_v1 import (
    build_trials, Grounded, GnocLikeTwin, sel_mfs, sel_ctx_label, sel_ctx_proto,
    score_arm, acc_vs_uniform, paired_word_boot,
)
import hdlab.grounded_similarity as GS
import numpy as np


def main() -> None:
    multi, _v1, census = load_multisense_eval()
    trials, mask_cache, sense_sents = build_trials(multi)
    gnoc = Grounded("GNOC")

    def ctx(tr):
        from experiments.exp_context_conditioned_sense_selection_v1 import masked_context_tokens
        return masked_context_tokens(tr["sentence"], mask_cache[tr["word"]])

    # info-free twin: fixed permutation of the grounded table (word -> another word's vector)
    tbl_words = sorted(GS._table().keys())
    perm = np.random.default_rng(20260826).permutation(len(tbl_words))
    sub = {tbl_words[i]: tbl_words[perm[i]] for i in range(len(tbl_words))}
    twin = GnocLikeTwin("GNOC", sub)

    # ---- (1) the prior works: MFS beats uniform CI-separated (corpus-free) --------------------
    mfs = score_arm(trials, lambda tr: sel_mfs(tr))
    mfs_vs_unif = acc_vs_uniform(mfs["rows"])
    print("[1] MFS micro=%.4f vs uniform=%.4f CI=%s sep_above=%s"
          % (mfs_vs_unif["micro_acc"], mfs_vs_unif["uniform_floor"], mfs_vs_unif["ci95"],
             mfs_vs_unif["CI_SEPARATED_ABOVE_UNIFORM"]))
    assert mfs_vs_unif["CI_SEPARATED_ABOVE_UNIFORM"], "the frequency prior must beat the uniform floor"

    # ---- (2) context-conditioned grounded is at chance on SUBORDINATE + ties its twin ---------
    gl = score_arm(trials, lambda tr: sel_ctx_label(tr, gnoc, ctx(tr)))
    tw = score_arm(trials, lambda tr: sel_ctx_label(tr, twin, ctx(tr)))
    sub_rows = [r for r in gl["rows"] if not r[2]]
    sub_gnoc = acc_vs_uniform(sub_rows)
    print("[2a] SUBORDINATE CTX_GNOC micro=%.4f vs uniform=%.4f sep_above=%s (n=%d)"
          % (sub_gnoc["micro_acc"], sub_gnoc["uniform_floor"],
             sub_gnoc["CI_SEPARATED_ABOVE_UNIFORM"], sub_gnoc["n_trials"]))
    assert not sub_gnoc["CI_SEPARATED_ABOVE_UNIFORM"], (
        "context-conditioned grounded selection must NOT beat chance on subordinate items "
        "(if it does, the offline win DID transfer -- update the verdict)")
    twin_delta = paired_word_boot(gl["rows"], tw["rows"])
    print("[2b] CTX_GNOC - TWIN_shuffle delta=%.4f CI=[%.4f,%.4f] (ties => no grounded signal)"
          % (twin_delta["delta"], twin_delta["ci_lo"], twin_delta["ci_hi"]))
    assert twin_delta["ci_lo"] <= 0 <= twin_delta["ci_hi"], (
        "the grounded context read-out must TIE its info-free twin here (no real signal); "
        "a CI-separated win over the twin would mean genuine grounded context signal")

    # ---- (3) the experience prototype is blind to rare (subordinate) senses --------------------
    proto = score_arm(trials, lambda tr: sel_ctx_proto(tr, gnoc, mask_cache[tr["word"]],
                                                       sense_sents[tr["word"]]))
    proto_dom = acc_vs_uniform([r for r in proto["rows"] if r[2]])
    proto_sub = acc_vs_uniform([r for r in proto["rows"] if not r[2]])
    print("[3] GNOC_PROTO dominant micro=%.4f sep_above=%s (n=%d) | subordinate n=%d"
          % (proto_dom["micro_acc"], proto_dom["CI_SEPARATED_ABOVE_UNIFORM"],
             proto_dom["n_trials"], proto_sub["n_trials"]))
    assert proto_dom["CI_SEPARATED_ABOVE_UNIFORM"], "the prototype must read DOMINANT senses above chance"
    assert proto_sub["n_trials"] <= 12, (
        "the subordinate prototype cell must be structurally tiny (rare senses have no held-out "
        "prototype); got n=%d" % proto_sub["n_trials"])

    # ---- (4) assert the landed corpus-dependent verdict + the associative-vs-grounded drill -----
    m = json.load(open(os.path.join(REPO_ROOT,
                  "data", "exp_context_conditioned_meaning_transfer_v1", "metrics.json"),
                  encoding="utf-8"))
    assert m["final_verdict"] == "OFFLINE_MEANING_WIN_DOES_NOT_TRANSFER_TO_CONTEXT_SELECTION", m["final_verdict"]
    drill = m["brain_drill_associative_vs_similarity"]
    # AT POWER (label population) the grounded vs associative channels are INDISTINGUISHABLE: the
    # well-powered fusion delta CI must include 0 (i.e. grounding neither clearly helps nor hurts the
    # associative channel). This DEMOTES the underpowered prototype 'grounding hurts' (-0.044, n=49).
    wp = drill["WELLPOWERED_FUSE_LABEL_minus_DIST_LABEL"]
    assert wp["ci_lo"] <= 0 <= wp["ci_hi"], ("at power, grounding must NOT be CI-separated from the "
                                             "associative channel (the 'grounding hurts' claim is "
                                             "underpowered): %r" % wp)
    # the distributional (associative) prototype reads DOMINANT senses above chance (re-finds frequency)
    ddp = m["splits_dominant_vs_subordinate"]["CTX_DIST_PROTO"]["dominant_congruent"]
    assert ddp["CI_SEPARATED_ABOVE_UNIFORM"], ddp
    # ROBUST: no context arm's OVERALL micro beats the frequency prior (MFS)
    mfs_micro = m["arms_micro"]["MFS_PRIOR"]["micro"]
    for a in ("CTX_GNOC_LABEL", "CTX_DIST_LABEL", "CTX_FUSE_LABEL", "CTXFREE_GNOC"):
        assert m["arms_micro"][a]["micro"] < mfs_micro, ("%s must not beat the frequency prior" % a)
    print("[4] landed verdict + drill consistent: AT POWER grounded vs associative INDISTINGUISHABLE "
          "(FUSE_LABEL-DIST_LABEL=%.4f CI[%.4f,%.4f]); associative prototype re-finds dominant "
          "senses (acc=%.4f); no context arm beats the frequency prior (%.4f)"
          % (wp["delta"], wp["ci_lo"], wp["ci_hi"], ddp["micro_acc"], mfs_micro))

    print("\nALL WITNESS ASSERTIONS PASSED")
    print("  The offline grounded (feature-similarity) meaning win does NOT transfer to context-")
    print("  conditioned selection. The working half is the frequency PRIOR (unwired); NO context")
    print("  channel (grounded OR associative) beats it, and at power the two channels are")
    print("  indistinguishable. The frequency-defeating (subordinate) items are data-starved here.")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
