"""Scaffold-free witness for `the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning`.

Reads the three landed metrics.json (no cell re-run, no scaffold) and asserts every load-bearing claim:
  A. NP-HEAD chunker is the live STRUCTURAL lever (compound RHR + genitive DP-head), CI-separated over the
     nearest-post-verbal position floor AND over its null, with the info-free CHUNK-SHUFFLE twin LOSING, holding
     on held-out doc halves, and NO modern regression.
  B. The morphological CASE cue is a faithfully-built, real cue (position-neutralized probe beats its info-free
     shuffle CI-sep) that is UNAVAILABLE on the canonical-active DO gold (0/669 orthogonal value; sparse decisive
     regime) -- a brain-faithful located negative (the Competition Model's own prediction).
  C. The IDEAL brain-faithful stack (NP-head chunk -> graded Competition-Model role assignment, the actual organ)
     reaches the same 0.98 (order-dominant), its shuffled-validity twin LOSES, an aggressive X-bar rule does NOT
     help (ceiling), and the residual is verb SUBCATEGORIZATION + gold-frame-errors, not more chunking.
  D. SIGNAL-LOSS LEDGER: on 19c prose our glass-box pipeline is AT/ABOVE a full modern parser (spaCy oracle),
     no signal is lost to pronoun filtering, and the residual attributes to POS-brittleness + verb-frame + clause.

Run: .venv/Scripts/python.exe verification/test_whodidwhat_nphead_case.py
"""
import json
import os

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(_REPO, "data")
PASS = 0


def _load(name):
    with open(os.path.join(DATA, name, "metrics.json"), encoding="ascii") as fh:
        return json.load(fh)["results"]


def ck(cond, msg):
    global PASS
    assert cond, "FAIL: " + msg
    PASS += 1
    print("  [OK] " + msg)


def main():
    nc = _load("exp_whodidwhat_nphead_case_v1")
    idl = _load("exp_whodidwhat_ideal_structural_v1")
    sl = _load("exp_whodidwhat_signal_loss_ledger_v1")

    print("A. NP-HEAD chunker -- the live structural lever")
    s = nc["selection_19c"]
    ck(s["n"] >= 600, "clean 19c direct-object gold n>=600 (n=%d)" % s["n"])
    ck(abs(s["acc_POS_NEAR"] - 0.9178) < 0.01, "position floor recomputed ~0.918 (=%.4f), matches parent" % s["acc_POS_NEAR"])
    ck(s["acc_NP_HEAD"] >= 0.975, "NP-head chunker reaches ~0.98 (=%.4f)" % s["acc_NP_HEAD"])
    d = s["NPHEAD_vs_NEAR"]
    ck(d["ci_lo"] > 0 and d["sep"], "NP-head beats floor CI-sep AND > null_p95 (d=%+.4f CI_lo=%+.4f null_p95=%.4f)" % (
        d["delta"], d["ci_lo"], d["null_p95"]))
    ck(d["half"] > 0, "CI half-width reported (%.4f)" % d["half"])
    cs = s["CHUNKSHUF_vs_NEAR"]
    ck(not (cs["ci_lo"] > 0), "info-free CHUNK-SHUFFLE twin does NOT beat the floor (d=%+.4f CI[%+.4f,%+.4f])" % (
        cs["delta"], cs["ci_lo"], cs["ci_hi"]))
    dc = s["NPHEAD_vs_CHUNKSHUF"]
    ck(dc["ci_lo"] > 0, "NP-head beats the CHUNK-SHUFFLE twin CI-sep (head info is real; d=%+.4f)" % dc["delta"])
    ck(s["heldout"]["A"]["ci_lo"] > 0 and s["heldout"]["B"]["ci_lo"] > 0,
       "lift holds on BOTH held-out doc halves (A_lo=%+.4f B_lo=%+.4f)" % (s["heldout"]["A"]["ci_lo"], s["heldout"]["B"]["ci_lo"]))
    m = nc["modern_no_regression"]
    ck(m["NPHEAD_vs_NEAR"]["ci_lo"] >= -0.005, "NO modern regression (qasrl n=%d, d=%+.4f CI_lo=%+.4f)" % (
        m["n"], m["NPHEAD_vs_NEAR"]["delta"], m["NPHEAD_vs_NEAR"]["ci_lo"]))

    print("B. CASE cue -- faithfully built, real, but structurally unavailable (located negative)")
    c = nc["case"]
    ck(c["gold_case_orthogonal_value"] == 0, "case has 0 orthogonal value on the canonical-active DO gold (0/%d)" % c["gold_n"])
    cv = c["CASE_vs_SHUFFLE"]
    ck(cv["ci_lo"] > 0, "case MECHANISM is real: position-neutralized CASE beats its info-free shuffle CI-sep (d=%+.4f)" % cv["delta"])
    ck(c["acc_CASE"] >= 0.95 and c["acc_CASE_SHUFFLE"] <= 0.6, "CASE=%.2f vs shuffle=%.2f (chance)" % (c["acc_CASE"], c["acc_CASE_SHUFFLE"]))
    ck(c["n_fronted_object_items"] < 0.01 * c["n_sentences_scanned"],
       "decisive (fronted-object) regime is sparse: %d in %d sentences (<1%%)" % (c["n_fronted_object_items"], c["n_sentences_scanned"]))

    print("C. IDEAL brain-faithful stack (NP-head -> graded Competition-Model role assignment)")
    ck(abs(idl["acc_IDEAL_comp"] - idl["acc_NP_HEAD"]) < 1e-6,
       "graded competition == NP-head on canonical DOs (order-dominant, %.4f)" % idl["acc_IDEAL_comp"])
    iv = idl["IDEAL_vs_SHUFVALID"]
    ck(iv["ci_lo"] > 0 and idl["acc_SHUFVALID_twin"] < 0.75,
       "shuffled-validity twin LOSES hard (twin=%.4f, IDEAL vs twin d=%+.4f CI-sep)" % (idl["acc_SHUFVALID_twin"], iv["delta"]))
    xv = idl["XBAR_vs_NPHEAD"]
    ck(not (xv["ci_lo"] > 0), "aggressive X-bar rule does NOT beat the simple chunker -- structural ceiling (d=%+.4f)" % xv["delta"])
    ck(idl["n_gold_frame_error"] >= 1, "residual contains GOLD-frame-errors where the chunker is PropBank-correct (%d)" % idl["n_gold_frame_error"])
    ck(idl["ceiling_gold_corrected"] >= idl["acc_IDEAL_comp"], "gold-corrected ceiling (%.4f) >= measured (%.4f)" % (
        idl["ceiling_gold_corrected"], idl["acc_IDEAL_comp"]))
    tax = idl["residual_taxonomy"]
    frame = tax.get("NAMING_OBJ_COMPLEMENT", 0) + tax.get("DITRANSITIVE", 0) + tax.get("GOLD_FRAME_ERROR_naming", 0) + tax.get("CLAUSE_BOUNDARY", 0)
    ck(frame >= idl["n_residual"] * 0.4, "the residual is dominated by verb SUBCATEGORIZATION frames (%d/%d)" % (frame, idl["n_residual"]))

    print("D. SIGNAL-LOSS LEDGER -- exactly where signal is lost vs the brain")
    ck(sl["POS_stage_recoverable"] <= 0.0, "no recoverable POS headroom: a modern tagger does NOT beat ours on 19c (%.4f)" % sl["POS_stage_recoverable"])
    ck(sl["parse_ceiling_headroom"] <= 0.0, "a FULL modern parser LOSES on 19c: we are at/above its ceiling (headroom=%.4f, spaCy=%.4f < ours=%.4f)" % (
        sl["parse_ceiling_headroom"], sl["acc_ORACLE_DOBJ_ceiling"], sl["acc_OURS"]))
    ck(sl["S3_pronoun_true_dobj_filtered"] == 0, "no who-did-what signal lost to pronoun (STOP) filtering on this gold (0)")
    att = sl["stage_loss_attribution"]
    ck(att.get("S5_VERB_FRAME", 0) >= 1, "residual attributes to the verb-frame stage (S5=%d)" % att.get("S5_VERB_FRAME", 0))
    ck(sum(att.values()) == sl["n_residual"], "every residual miss is attributed to a stage (%d)" % sl["n_residual"])

    print("E. DOWNSTREAM -- the wire fixes the live consumers (WIRE-DON'T-ISLAND)")
    dn = _load("exp_whodidwhat_downstream_live_reader_v1")
    ck(dn["acc_LANDED_resolve_patient"] < 0.75, "the LANDED role assigner is FAR from peak on clean 19c DOs (%.4f)" % dn["acc_LANDED_resolve_patient"])
    ck(dn["NPHEAD_vs_LANDED_resolve"]["ci_lo"] > 0.2, "NP-head recovers a LARGE downstream gap (+%.4f CI-sep)" % dn["NPHEAD_vs_LANDED_resolve"]["delta"])
    ck(dn["landed_miss_nphead_share"] >= 0.9, "the NP-head error is the DOMINANT landed error mode (%.0f%% of misses)" % (100 * dn["landed_miss_nphead_share"]))
    ck(dn["wired_miss_nphead_share"] >= 0.9, "same for the recorded LIVE reader (%.0f%% of its misses are NP-head)" % (100 * dn["wired_miss_nphead_share"]))
    ck(dn["acc_NP_HEAD_on_abstained"] >= 0.9, "the 22%% the live reader ABSTAINS on are answerable: chunker gets %.4f on them (lost coverage, not hard)" % dn["acc_NP_HEAD_on_abstained"])
    ck(dn["EFFECTIVE_ideal_vs_live"]["ci_lo"] > 0.3, "EFFECTIVE end-to-end (abstention=wrong): ideal %.4f vs live %.4f, +%.4f CI-sep" % (
        dn["EFFECTIVE_ideal_all"], dn["EFFECTIVE_live_reader_all"], dn["EFFECTIVE_ideal_vs_live"]["delta"]))

    pc = _load("exp_whodidwhat_per_consumer_wire_v1")
    ck(pc["route_theme_equals_hybrid_landed"] == pc["n"], "route_predicate_arguments delegates its theme to hybrid_role_patient (%d/%d)" % (pc["route_theme_equals_hybrid_landed"], pc["n"]))
    for k, c in pc["consumers"].items():
        ck(c["IMPROVED_vs_LANDED"]["sep"], "consumer %s improves with the wire CI-sep (%.4f -> %.4f)" % (k, c["acc_LANDED"], c["acc_IMPROVED"]))
        ck(not c["TWIN_vs_LANDED"]["sep"], "consumer %s info-free twin does NOT recover (%.4f)" % (k, c["acc_INFOFREE_TWIN"]))

    ic = _load("exp_whodidwhat_improved_consumer_v1")
    ck(ic["COMBINED_vs_LANDED"]["ci_lo"] > 0.25, "the COMBINED full stack is FAR better than landed (%.4f vs %.4f, +%.4f CI-sep)" % (
        ic["acc_COMBINED_full_stack"], ic["acc_LANDED"], ic["COMBINED_vs_LANDED"]["delta"]))

    print("F. THE FULL FIX (one drop-in path: coverage + NP-head + graded competition + dormant case)")
    ff = _load("exp_whodidwhat_full_fix_v1")
    ck(ff["acc_FULL_FIX"] >= 0.97 and ff["coverage_FULL_FIX"] == 1.0, "full fix: acc=%.4f at 100%% coverage" % ff["acc_FULL_FIX"])
    ck(ff["FULLFIX_vs_LIVE"]["ci_lo"] > 0.3, "full fix beats the live reader end-to-end +%.4f CI-sep (%.4f -> %.4f)" % (
        ff["FULLFIX_vs_LIVE"]["delta"], ff["acc_LIVE_effective"], ff["acc_FULL_FIX"]))
    ck(ff["FULLFIX_vs_TWIN"]["ci_lo"] > 0.3 and ff["acc_INFOFREE_TWIN"] < 0.65, "full fix beats its info-free twin CI-sep (twin=%.4f)" % ff["acc_INFOFREE_TWIN"])

    print("G. SECOND-PASS FOLLOW-ON -- the mention path (situation_reader._assign_roles) gets the SAME rule")
    mp = _load("exp_whodidwhat_mention_path_fix_v1")
    ck(mp["FIXED_vs_LANDED"]["ci_lo"] > 0.1, "mention-level NP-head reduction lifts the LANDED _assign_roles CI-sep (%.4f -> %.4f, +%.4f)" % (
        mp["acc_LANDED_mention_path"], mp["acc_FIXED_mention_path"], mp["FIXED_vs_LANDED"]["delta"]))
    ck(not mp["TWIN_vs_LANDED"]["sep"], "the mention-path info-free twin does NOT recover (%.4f)" % mp["acc_INFOFREE_TWIN"])

    print("\n[witness] %d/%d checks PASS" % (PASS, PASS))


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
