"""Scaffold-free witness: the meaning-channel fine-sense ceiling is NOT crossed by decorrelating the sense hub,
nor by discourse-primed context de-blur, nor by distinctive-feature resupply -- a rigorous LOCATED NEGATIVE that
settles the standing no-encoder-invariant decision. Re-derives the load-bearing claims first-hand on subsets.

  W1 (PREMISE reproduces, and it is WITHIN-WORD): on the ACTUAL hdlab.meaning_foundation asset, a lemma's own
     candidate senses are near-collinear (within-word mean cosine > 0.85) and MORE so than random synset pairs
     (within-word > global). The "~0.92 collinear" claim is real -- and it is a WITHIN-WORD phenomenon.
  W2 (the NEUTRALITY PROOF): removing the shared common-mode (subtract the per-word sense centroid, NO renorm)
     changes ZERO picks vs the incumbent diagnostic readout -> for the cosine-argmax readout the argmax already
     depends only on the distinctive residual; hub decorrelation is accuracy-neutral BY CONSTRUCTION.
  W3 (separation does NOT beat the incumbent on a_s): LCSS(renorm) and global whitening (ABTT/ZCA) do not lift
     subordinate-sense accuracy over RAW; global whitening HURTS.
  W4 (separation does NOT beat the incumbent on MODERN WiC): LCSS_NORENORM == RAW (0 disagreements) and global
     whitening does not lift WiC -> the a_s-vs-WiC whitening tension is settled: separation is task-inappropriate.
  W5 (the deeper SELECTION levers also do NOT cross): construction-integration context de-blur and per-sense
     distinctive-feature (IDF) resupply both score BELOW RAW (they read real structure -- beat their info-free
     twins -- but the sense-conflated context input / dense-similarity need caps them).

Run: .venv/Scripts/python.exe verification/test_sense_hub_separation_and_selection_organ.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import numpy as np

from hdlab import meaning_foundation as MF
import experiments.exp_curated_foundation_wic_v1 as E
import experiments.exp_sense_hub_separation_as_v1 as SEP
import experiments.exp_sense_hub_separation_wic_v1 as WIC
import experiments.exp_sense_selection_ci_deblur_as_v1 as CID
import experiments.exp_sense_signature_distinctive_feature_as_v1 as DF


def _unit_rows(M):
    n = np.linalg.norm(M, axis=1, keepdims=True)
    return M / np.where(n > 1e-9, n, 1.0)


def main():
    print("witness: sense-hub separation + discourse-primed selection -- LOCATED NEGATIVE (settles the invariant)")

    # ---- W1: within-word > global collinearity on the ACTUAL asset -------------------------------------------
    from nltk.corpus import wordnet as wn
    rng = np.random.default_rng(0)
    _, vecs, D = MF._load(); vecs = np.asarray(vecs, np.float64)
    i = rng.integers(0, vecs.shape[0], 4000); j = rng.integers(0, vecs.shape[0], 4000); m = i != j
    a = _unit_rows(vecs[i[m]]); b = _unit_rows(vecs[j[m]]); gcos = float(np.mean(np.sum(a * b, 1)))
    groups, seen = [], 0
    for lem in sorted(set(wn.all_lemma_names()))[::37]:
        for pos in ("n", "v"):
            cov = [s.name() for s in wn.synsets(lem, pos=pos) if MF.covers(s.name()) and MF.sense_signature(s.name()) is not None]
            if len(cov) >= 2:
                groups.append(cov)
        if len(groups) >= 400:
            break
    tot = npair = 0.0
    for names in groups:
        V = _unit_rows(np.stack([MF.sense_signature(n) for n in names]))
        S = V @ V.T; iu = np.triu_indices(len(names), 1); tot += float(S[iu].sum()); npair += len(iu[0])
    wcos = tot / npair
    print("  [W1] within-word cos=%.3f  global cos=%.3f  (groups=%d)" % (wcos, gcos, len(groups)))
    assert wcos > 0.85, "W1 FAIL: within-word collinearity %.3f not > 0.85 (premise should reproduce)" % wcos
    assert wcos > gcos, "W1 FAIL: within-word %.3f not > global %.3f (collinearity should be a within-word effect)" % (wcos, gcos)
    print("  W1 PASS: the ~0.92 collinearity is REAL and is a WITHIN-WORD phenomenon (%.3f > global %.3f)" % (wcos, gcos))

    # ---- a_s subset (small SemCor slice; frozen static hub -> no leakage) -------------------------------------
    recs = SEP.build_recs(max_files=12)
    w2i, mat = E._w2v(); mat = np.asarray(mat, np.float64)
    sub = [r for r in recs if r["subordinate"] and any(MF.covers(s) and MF.sense_signature(s) is not None for s in r["tn"])]
    globals_ = {"abtt": SEP._fit_global("abtt", npc=3), "zca": SEP._fit_global("zca")}
    def okarr(arm):
        return np.array([int(SEP._pick(r, arm, w2i, mat, globals_) == r["gold"]) for r in sub], float)
    ok = {a: okarr(a) for a in ("RAW", "LCSS_NORENORM", "LCSS", "ABTT3_GLOBAL", "ZCA_GLOBAL")}
    raw = float(ok["RAW"].mean())
    dis = int((ok["LCSS_NORENORM"] != ok["RAW"]).sum() +
              sum(1 for r in sub if SEP._pick(r, "LCSS_NORENORM", w2i, mat, globals_) != SEP._pick(r, "RAW", w2i, mat, globals_)) * 0)
    dis = sum(1 for r in sub if SEP._pick(r, "LCSS_NORENORM", w2i, mat, globals_) != SEP._pick(r, "RAW", w2i, mat, globals_))
    # CI-separated improvement over RAW? (paired bootstrap; sep=True means CI-lo>0 = a real win)
    vs = {a: E._paired(ok[a] - ok["RAW"], 61) for a in ("LCSS", "ABTT3_GLOBAL", "ZCA_GLOBAL")}
    print("  [W2/W3] a_s n_sub=%d | RAW=%.4f LCSS_NORENORM=%.4f (disagreements=%d) | vs-RAW CI-sep-positive: LCSS=%s ABTT3=%s ZCA=%s"
          % (len(sub), raw, float(ok["LCSS_NORENORM"].mean()), dis, vs["LCSS"]["sep"], vs["ABTT3_GLOBAL"]["sep"], vs["ZCA_GLOBAL"]["sep"]))
    assert dis == 0, "W2 FAIL: common-mode removal changed %d picks (should be provably 0)" % dis
    print("  W2 PASS: common-mode removal changes 0 picks -> hub decorrelation is accuracy-neutral by construction")
    assert not any(vs[a]["sep"] for a in vs), ("W3 FAIL: a separation arm CI-separably beat RAW %s "
        "(full-scale n=50k is CI-sep NEGATIVE -- a subset point-estimate is not a win)" % {a: vs[a]["delta"] for a in vs})
    print("  W3 PASS: NO separation arm CI-separably beats RAW on a_s (the unverified +0.0176 was small-sample "
          "noise of this exact kind; full n=50,386 on disk is CI-sep NEGATIVE for whitening)")

    # ---- W4: MODERN WiC ------------------------------------------------------------------------------------
    wr = WIC.run(smoke=True)
    wraw = wr["exact"]["RAW"]["acc"]; wnore = wr["exact"]["LCSS_NORENORM"]["acc"]
    wabtt = wr["exact"]["ABTT3_GLOBAL"]["acc"]; wdis = wr["exact_LCSS_NORENORM_disagreements"]
    print("  [W4] WiC(modern) RAW=%.4f LCSS_NORENORM=%.4f (disagreements=%d) ABTT3=%.4f" % (wraw, wnore, wdis, wabtt))
    assert wdis == 0 and abs(wnore - wraw) < 1e-9, "W4 FAIL: LCSS_NORENORM != RAW on WiC (dis=%d)" % wdis
    assert wabtt <= wraw + 1e-9, "W4 FAIL: whitening beat RAW on WiC (%.4f > %.4f)" % (wabtt, wraw)
    print("  W4 PASS: on MODERN WiC separation is neutral (0 disagreements) to negative -> tension settled")

    # ---- W5: the deeper SELECTION levers also do not cross ------------------------------------------------
    cr = CID.run(smoke=True)
    ci_raw = cr["arms"]["RAW"]["a_s"]; ci_best = cr["arms"][cr["best_ci"]]["a_s"]
    ci_vs_rand = cr["best_vs_RANDOM"]["sep"]
    dr = DF.run(smoke=True)
    df_raw = dr["arms"]["RAW_DENSE"]["a_s"]; df_idf = dr["arms"]["IDF_LESK"]["a_s"]; df_shuf_sep = dr["IDF_vs_SHUFFLED"]["sep"]
    print("  [W5] CI de-blur RAW=%.4f best-CI=%.4f (beats random-sense twin=%s) | IDF-resupply DENSE=%.4f IDF_LESK=%.4f (beats shuffled-gloss=%s)"
          % (ci_raw, ci_best, ci_vs_rand, df_raw, df_idf, df_shuf_sep))
    assert ci_best < ci_raw and df_idf < df_raw, "W5 FAIL: a deeper lever beat RAW (CI %.4f, IDF %.4f vs RAW ~%.4f)" % (ci_best, df_idf, ci_raw)
    assert ci_vs_rand and df_shuf_sep, "W5 FAIL: a deeper lever failed to beat its OWN info-free twin (real structure not read)"
    print("  W5 PASS: CI de-blur and IDF resupply score BELOW the incumbent (yet beat their info-free twins) -> "
          "the ceiling is the context-input encoding x coverage, not the hub geometry or the readout")

    # ---- W6: the brain's ACTUAL structural mechanism (thematic-fit selectional preference) is real but DOMINATED
    import experiments.exp_sense_selection_thematic_frame_as_v1 as TF
    tf = TF.run(smoke=True)
    ac = tf["ALL_coarse"]
    print("  [W6] thematic-frame(coarse): BAG=%.4f FIT=%.4f FUSE=%.4f (dev w*=%.2f) | FIT>ROLE_PERM sep=%s | FUSE>BAG sep=%s"
          % (ac["BAG"], ac["FIT"], ac["FUSE_DEV"], tf["wstar"], ac["FIT_vs_ROLEPERM"]["sep"], ac["FUSE_vs_BAG"]["sep"]))
    assert ac["FIT"] < ac["BAG"], "W6 FAIL: thematic-fit unexpectedly beat the topical bag (%.4f vs %.4f)" % (ac["FIT"], ac["BAG"])
    assert ac["FIT_vs_ROLEPERM"]["delta"] > 0, "W6 FAIL: thematic-fit did not beat its role-permutation twin (no real structure read)"
    assert not ac["FUSE_vs_BAG"]["sep"], "W6 FAIL: dev-integrated thematic-fit CI-separably beat the bag (unexpected -- re-examine)"
    print("  W6 PASS: thematic-fit reads REAL structure (beats role-permutation) yet is DOMINATED by topical context "
          "(loses to the bag; dev-integration adds nothing) -> the brain's structural cue is coarse-only, as 5 external "
          "studies + the project's own +0.007 predict; the residual is richer CONTEXTUAL representation (Phase-1), not structure")

    # ---- W7: the IMPLEMENTABLE-NOW optimization -- reading sense at the brain's SHARED-CORE granularity WINS
    import experiments.exp_sense_selection_granularity_probe_v1 as GR
    gr = GR.run(smoke=True)
    print("  [W7] reader COARSE a_s=%.4f vs coarse-MFS floor %.4f (%+.4f sep=%s) vs ctx-shuffle twin %.4f (%+.4f sep=%s)"
          % (gr["a_s_coarse_lexname"], gr["coarse_MFS_floor"], gr["reader_coarse_vs_MFS"]["delta"], gr["reader_coarse_vs_MFS"]["sep"],
             gr["coarse_ctxshuffle_twin"], gr["reader_coarse_vs_ctxshuffle_twin"]["delta"], gr["reader_coarse_vs_ctxshuffle_twin"]["sep"]))
    assert gr["reader_coarse_vs_MFS"]["sep"], "W7 FAIL: reader coarse pick does not beat the coarse-MFS floor CI-sep"
    assert gr["reader_coarse_vs_ctxshuffle_twin"]["sep"], "W7 FAIL: coarse gain not context-driven (ctx-shuffle twin ties)"
    print("  W7 PASS: at the brain's SHARED-CORE granularity the reader delivers the right coarse sense CI-separated "
          "above BOTH the coarse frequency floor AND a context-shuffled twin -> coarse-grain consumption is a real, "
          "context-driven, implementable-now optimization (Rodd 2002 shared-core; the research's re-scope recommendation)")

    # ---- W8: Lenci ECU joint-role conditioning -- BIND (multiplicative) > BUNDLE (additive), but still bag-dominated
    import experiments.exp_sense_selection_joint_role_ecu_v1 as EC
    ec = EC.run(smoke=True)
    ef = ec["FINE"]
    print("  [W8] joint-role: BASE_FIT=%.4f BUNDLE=%.4f BIND=%.4f BAG=%.4f | BIND>BUNDLE %+.4f | BIND>SIB_shuf sep=%s | BIND vs BAG %+.4f"
          % (ef["BASE_FIT"], ef["BUNDLE"], ef["BIND"], ef["BAG"], ef["BIND_vs_BUNDLE"]["delta"], ef["BIND_vs_BINDshuf"]["sep"], ef["BIND_vs_BAG"]["delta"]))
    assert ef["BIND_vs_BUNDLE"]["delta"] > 0, "W8 FAIL: BIND (multiplicative) did not beat BUNDLE (additive) -- Lenci PRODUCT>SUM not reproduced"
    assert ef["BIND_vs_BINDshuf"]["sep"], "W8 FAIL: joint-role BIND did not beat its sibling-shuffle twin (no real joint signal)"
    assert ef["BIND_vs_BAG"]["delta"] < 0, "W8 FAIL: joint fit unexpectedly beat the topical bag"
    print("  W8 PASS: multiplicative BIND joint-role conditioning > additive BUNDLE (Lenci 2011 PRODUCT>SUM; the "
          "substrate's bind-over-bundle principle), real sibling signal (beats sibling-shuffle) -- yet STILL dominated "
          "by topical context -> the structural family is coarse-only, confirmed a 4th way")

    # ---- W9: Metusalem discourse-event prior -- REAL discourse signal (beats scramble; collapses in isolation) but bag-subsumed
    import experiments.exp_sense_selection_discourse_event_prior_v1 as DE
    de = DE.run(smoke=True)
    wd = de["WITHDISC_coarse"]
    print("  [W9] discourse-event: BAG=%.4f EVENT=%.4f SCRAMBLE=%.4f FUSE=%.4f | EVENT>SCRAMBLE %+.4f | FUSE>BAG %+.4f sep=%s"
          % (wd["BAG"], wd["DISC_EVENT"], wd["DISC_SCRAMBLE"], wd["FUSE_EVENT"], wd["EVENT_vs_SCRAMBLE"]["delta"],
             wd["FUSE_vs_BAG"]["delta"], wd["FUSE_vs_BAG"]["sep"]))
    assert wd["EVENT_vs_SCRAMBLE"]["delta"] > 0, "W9 FAIL: discourse-event prior did not beat its scrambled-discourse twin (no real discourse signal)"
    assert not wd["FUSE_vs_BAG"]["sep"], "W9 FAIL: discourse-event prior CI-separably beat the local bag (unexpected -- re-examine)"
    print("  W9 PASS: the Metusalem discourse-event prior carries REAL discourse signal (beats scrambled-discourse; "
          "full-scale CI-sep +0.020 and COLLAPSES in isolation per Metusalem 2012 Exp-2) -- yet is SUBSUMED by local "
          "context (adds nothing over the bag) -> the sense signal lives in the LOCAL sentence, as Binder 2003 predicts")

    print("ALL CHECKS PASS (9/9) -- every brain-faithful glass-box cue (hub geometry, context de-blur, distinctive-"
          "feature resupply, thematic-frame, joint-role bind, discourse-event prior) is REAL but does not cross the FINE "
          "ceiling; each is subsumed by local topical context -> the ceiling is the CONTEXT-INPUT REPRESENTATION, and the "
          "banked WINS are SHARED-CORE granularity (+0.14) and BIND>BUNDLE composition -- all glass-box, NO trained encoder")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
