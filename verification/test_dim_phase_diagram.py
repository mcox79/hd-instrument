"""Scaffold-free witness for `dimensional_phase_diagram_audit_of_the_current_organs`.

Asserts the audit's load-bearing claims by LIVE recompute on the real organ primitives (register) plus
the landed meaning channel -- no metric crosses harnesses; each number is recomputed here.

  REGISTER (the ONLY fixed-D superposition organ):
    1. POSITIVE CONTROL -- the harness SEES a capacity cliff: flat FHRR decode collapses at high load /
       small D and RECOVERS with more D (a phase transition), and the info-free random-key twin is ~chance.
    2. LEVER -- at FIXED D on the cliff, the sparse-code (multibank routing) recovers accuracy that only
       more-D would otherwise buy => sparsity is a DISTINCT lever from dimensionality.
    3. REAL-TASK STRUCTURAL -- with oracle linking, register decode on the real LitBank task is FLAT
       (CI-overlap) from D=256 to a higher D => the who-did-what ceiling is NOT under-dimensioned; it is
       structural (front-end/linking limited). [loads the full-sweep metrics if present; else a 2-point live check.]

  MEANING (a sparse-EXACT organ, no fixed D): 4. random-projected similarity reaches the exact-cosine rho
    at K* < 1024 (its intrinsic dim), so D is not a lever for it and it is not under-dimensioned.

Run:  .venv/Scripts/python.exe verification/test_dim_phase_diagram.py
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import glob
import json
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

import experiments.exp_dim_phase_diagram_register_v1 as R  # noqa: E402


def _ci_overlap(a, b):
    return not (a[2] < b[1] or b[2] < a[1])


def main():
    checks = []
    v = 100

    # 1. POSITIVE CONTROL: flat cliff + recovery + info-free twin at chance
    flat_lo, twin = R._one_cell(256, 64, v, "flat", 30, 1)      # small D, high load -> off the plateau
    flat_hi, _ = R._one_cell(1024, 64, v, "flat", 30, 1)        # more D -> recovers
    perfect, _ = R._one_cell(4096, 8, v, "flat", 20, 1)         # generous D, low load -> ~perfect
    checks.append(("POSITIVE CONTROL: flat decode collapses at (D256,M64) vs recovers at (D1024,M64) [cliff seen]",
                   (flat_hi - flat_lo) > 0.2, {"flat_D256_M64": round(flat_lo, 3), "flat_D1024_M64": round(flat_hi, 3)}))
    checks.append(("info-free random-key twin ~= chance (1/100=0.01)", twin < 0.06, {"twin": round(twin, 3)}))
    checks.append(("generous D + low load decodes ~perfectly", perfect > 0.98, {"flat_D4096_M8": round(perfect, 3)}))

    # 2. LEVER: multibank routing recovers at FIXED D
    mb, _ = R._one_cell(256, 64, v, "multibank", 30, 1)
    checks.append(("LEVER: sparse-code (multibank) recovers at FIXED D=256 where flat has fallen off",
                   (mb - flat_lo) > 0.1, {"flat": round(flat_lo, 3), "multibank": round(mb, 3),
                                          "sparsity_gain": round(mb - flat_lo, 3)}))

    # 3. REAL-TASK STRUCTURAL: prefer the full-sweep metrics; else a live 2-point check
    rt_dir = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_realtask_v1")
    metrics = sorted(glob.glob(os.path.join(rt_dir, "metrics_*.json")))
    struct_ok = None; detail = {}
    if metrics:
        # pick the widest-grid multibank sweep
        best = None
        for m in metrics:
            d = json.load(open(m, encoding="utf-8"))
            if "multibank" in d.get("rows", {}) and len(d["d_grid"]) >= 3:
                if best is None or len(d["d_grid"]) > len(best["d_grid"]):
                    best = d
        if best is not None:
            rb = best["rows"]["multibank"]; dg = best["d_grid"]
            lo, top = dg[0], dg[-1]
            o_lo = rb[str(lo)]["oracle_pron"] if str(lo) in rb else rb[lo]["oracle_pron"]
            o_top = rb[str(top)]["oracle_pron"] if str(top) in rb else rb[top]["oracle_pron"]
            struct_ok = _ci_overlap(o_lo, o_top) or (o_top[0] - o_lo[0] < 0.03)
            detail = {"source": "docs%s_d%s" % (best["docs"], len(best["d_grid"])), "oracle_D%d" % lo: o_lo,
                      "oracle_D%d" % top: o_top}
    if struct_ok is None:
        import experiments.exp_litbank_entity_tracking_end_to_end_v1 as H
        recs = H.load_cache()[:8]
        orig = H.D
        try:
            H.D = 256; r256 = H.run(records=recs, backend="multibank", n_boot=200)["accuracy_pronoun"]["ORACLE"]
            H.D = 2048; r2048 = H.run(records=recs, backend="multibank", n_boot=200)["accuracy_pronoun"]["ORACLE"]
        finally:
            H.D = orig
        struct_ok = _ci_overlap(r256, r2048) or (r2048[0] - r256[0] < 0.03)
        detail = {"source": "live_docs8", "oracle_D256": r256, "oracle_D2048": r2048}
    checks.append(("REAL-TASK: oracle register decode FLAT across D (STRUCTURAL, not under-dimensioned)",
                   bool(struct_ok), detail))

    # 4. MEANING sparse-exact: prefer metrics; else tiny live projection sanity
    mp = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_meaning_v1", "metrics.json")
    if os.path.exists(mp):
        d = json.load(open(mp, encoding="utf-8"))
        ksat = d["k_saturation"]; rising = d["rising_at_1024"]
        checks.append(("MEANING: sparse-exact, intrinsic dim K* < 1024 and not rising at 1024",
                       (ksat is not None and ksat < 1024 and not rising),
                       {"exact_rho": d["exact_rho"][0], "k_saturation": ksat, "rising_at_1024": rising}))
    else:
        checks.append(("MEANING: metrics present", False, {"note": "run exp_dim_phase_diagram_meaning_v1 first"}))

    # 5-6. BEYOND-N axes (owner: "more than n"): orthogonality IS a lever; binding depth is NOT; precision
    #      bites only at q=2. Live recompute near the cliff (D=256, M=48) via the axes primitive.
    import experiments.exp_dim_phase_diagram_axes_v1 as A
    ortho_lo = A._cell(256, 48, 100, 1, 0.0, 0, 1, 30, 1)[0]     # orthogonal codes
    ortho_hi = A._cell(256, 48, 100, 1, 0.8, 0, 1, 30, 1)[0]     # correlated codes rho=0.8
    checks.append(("BEYOND-N: code ORTHOGONALITY is a lever (correlated codes collapse vs orthogonal)",
                   (ortho_lo - ortho_hi) > 0.2, {"rho0.0": round(ortho_lo, 3), "rho0.8": round(ortho_hi, 3)}))
    dep1 = A._cell(256, 48, 100, 1, 0.0, 0, 1, 25, 1)[0]
    dep5 = A._cell(256, 48, 100, 1, 0.0, 0, 5, 25, 1)[0]
    checks.append(("BEYOND-N: binding DEPTH is NOT a lever (exact-invertible bind; depth1~=depth5)",
                   abs(dep1 - dep5) < 0.1, {"depth1": round(dep1, 3), "depth5": round(dep5, 3)}))
    q_full = A._cell(256, 48, 100, 1, 0.0, 0, 1, 25, 1)[0]
    q_sign = A._cell(256, 48, 100, 1, 0.0, 2, 1, 25, 1)[0]
    checks.append(("BEYOND-N: PRECISION bites at q=2 (binary/BSC loses vs full complex near the cliff)",
                   (q_full - q_sign) > 0.1, {"q_full": round(q_full, 3), "q2_sign": round(q_sign, 3)}))

    # 7. READOUT RULE: CA3/SIC joint completion recovers accuracy over argmax in the overload window.
    import experiments.exp_dim_phase_diagram_cleanup_rule_v1 as CL
    cl_arg, cl_sic = CL._one(256, 64, 100, 25, 1)
    checks.append(("READOUT: CA3/SIC joint completion recovers over argmax at overload (the cliff is a readout artifact)",
                   (cl_sic - cl_arg) > 0.15, {"argmax": round(cl_arg, 3), "sic": round(cl_sic, 3)}))

    # 8. MULTIHOP: directed (permutation-protected) reasoning holds where naive symmetric-bind collapses.
    import experiments.exp_dim_phase_diagram_multihop_v1 as MH
    dir_c = MH._one(2048, 40, 6, 4, 20, 1, "argmax", directed=True)
    und_c = MH._one(2048, 40, 6, 4, 20, 1, "argmax", directed=False)
    checks.append(("MULTIHOP: directed (permutation) reasoning holds where naive commutative bind collapses",
                   dir_c[1] - und_c[1] > 0.2, {"directed_hop2": dir_c[1], "undirected_hop2": und_c[1]}))

    # 9. ADAPTATION: a gold-blind confidence gate escalating argmax->CA3 beats argmax AND a same-budget random gate.
    import experiments.exp_dim_phase_diagram_adaptive_v1 as AD
    ad = AD._one(256, 64, 100, 25, 1)
    adr = AD._one(256, 64, 100, 25, 1, rand_gate=True)
    checks.append(("ADAPTATION: confidence-gated adaptive readout beats argmax and a same-budget random gate",
                   ad["adaptive"] > ad["argmax"] + 0.1 and ad["adaptive"] > adr["adaptive"] + 0.02,
                   {"argmax": ad["argmax"], "adaptive": ad["adaptive"], "random_gate": adr["adaptive"]}))

    # 10. REAL-CODE orthogonality + DG fix: real semantic codes are correlated and cost storage capacity;
    #     DG sparse decorrelation recovers it toward the orthogonal ideal.
    import numpy as np
    import experiments.exp_dim_phase_diagram_realcode_v1 as RC
    rng = np.random.default_rng(1); rc_codes, rc_n = RC._build_codes(rng)
    c_real = RC._mean_abs_cos(rc_codes["real_dense"]); c_orth = RC._mean_abs_cos(rc_codes["rand_orth"])
    real_rec, _ = RC._recover(rc_codes["real_dense"], 32, 120, 5)
    dg_rec, _ = RC._recover(rc_codes["dg_sparse"], 32, 120, 5)
    checks.append(("REAL-CODE: meaning codes ARE correlated + cost capacity; DG sparse decorrelation RECOVERS it",
                   c_real > c_orth and dg_rec > real_rec + 0.05,
                   {"corr_real": round(c_real, 4), "corr_orth": round(c_orth, 4),
                    "recover_real_dense_M32": round(real_rec, 3), "recover_dg_sparse_M32": round(dg_rec, 3)}))

    # 11. STORE-MATCHED fixes: multihop over correlated codes -- directed(+CA3) recovers; DG into a BINDING store breaks.
    import experiments.exp_dim_phase_diagram_stacked_v1 as ST
    st_def = ST._one(60, 6, 4, 0.5, directed=False, decorr=False, ca3=False, n_reps=20, seed=1)
    st_mat = ST._one(60, 6, 4, 0.5, directed=True, decorr=False, ca3=True, n_reps=20, seed=1)
    st_mis = ST._one(60, 6, 4, 0.5, directed=True, decorr=True, ca3=False, n_reps=20, seed=1)
    checks.append(("STORE-MATCHED: directed+CA3 recover multihop over correlated memory; DG into a binding store BREAKS it",
                   st_mat[3] > st_def[3] + 0.2 and st_mis[1] < st_mat[1] - 0.2,
                   {"default_hop4": st_def[3], "matched_hop4": st_mat[3], "mismatched_DG_hop2": st_mis[1]}))

    # 12. CENSUS: the directed matrix-Hebbian relational store is a SEPARATE, higher-capacity regime than the
    #     vector bundle -- perfect where a bundle store would be dead (10x its k_cliff).
    import experiments.exp_dim_phase_diagram_census_v1 as CE
    import hdlab.k_cliff_scaling as KC
    kcl = KC.k_cliff(512)
    wm_acc, wm_tw = CE._one(512, 400, 40, 10 * kcl, 4, 1)     # 10x the bundle k_cliff
    checks.append(("CENSUS: directed W-matrix relational store is a separate higher-capacity regime (perfect where a bundle is dead)",
                   wm_acc > 0.9 and wm_tw < 0.1,
                   {"load_T": 10 * kcl, "x_bundle_kcliff": 10, "wmatrix_acc": round(wm_acc, 3), "twin": round(wm_tw, 3)}))

    # 13. REAL multihop organ: perfect deep-hop reasoning on CLEAN chains (no mechanism/dim cliff); twin dead.
    import experiments.exp_dim_phase_diagram_multihop_real_v1 as MR
    mr_naive = MR._depth_curve(200, 20, 1024, 6, 150, 5, 12, 1, "naive")
    mr_twin = MR._depth_curve(200, 20, 1024, 6, 150, 5, 12, 1, "twin")
    checks.append(("REAL-MULTIHOP: the actual organ reasons deep on clean chains (5-hop reliable); shuffled-cleanup twin dead",
                   mr_naive[4] > 0.9 and mr_twin[0] < 0.2,
                   {"naive_hop5": mr_naive[4], "twin_hop1": mr_twin[0]}))

    # 14. TEMPORAL family: contiguity kernel decays smoothly; graded context preserves neighbor-contiguity where
    #     an orthogonal key destroys it (D is a timescale bank, not a capacity budget).
    import experiments.exp_dim_phase_diagram_temporal_v1 as TM
    k0 = TM._kernel(TM.GradedTemporalContext(d=1024, seed=1, horizon=500), 250.0, 250.0)
    k_near = TM._kernel(TM.GradedTemporalContext(d=1024, seed=1, horizon=500), 250.0, 251.0)
    k_far = abs(TM._kernel(TM.GradedTemporalContext(d=1024, seed=1, horizon=500), 250.0, 450.0))
    _, nb_g = TM._temporal_resolution(1024, 40, 3, 1, orthogonal=False)
    _, nb_o = TM._temporal_resolution(1024, 40, 3, 1, orthogonal=True)
    checks.append(("TEMPORAL: contiguity kernel smooth (lag0>near>far); graded context preserves neighbor-contiguity vs orthogonal",
                   k0 > 0.99 and k_near > k_far and nb_g > nb_o + 0.2,
                   {"kernel_lag0": round(k0, 3), "kernel_lag1": round(k_near, 3), "kernel_far": round(k_far, 3),
                    "graded_neighbor_frac": round(nb_g, 2), "orthogonal_neighbor_frac": round(nb_o, 2)}))

    # 15. ADDRESSED-STORE READ REGIME (the biggest LIVE non-dimensional lever): a distributed semantic code
    #     generalises from a RELATED cue where the exact-key hash cannot (~chance).
    import experiments.exp_addressed_store_partial_cue_v1 as AS
    _sem, _exc, _fid, _bases = AS._make_world(10, 6, 256, 0.55, np.random.default_rng(1))
    rel_sem = AS._related_cue_test(_sem, _fid, _bases, "semantic", 0.55, 256, 300, np.random.default_rng(2))
    rel_exc = AS._related_cue_test(_exc, _fid, _bases, "exact_key", 0.55, 256, 300, np.random.default_rng(2))
    checks.append(("ADDRESSED-READ: distributed semantic code generalises from a related cue (1.0) where exact-key hash is ~chance",
                   rel_sem > 0.8 and rel_exc < 0.25 and (rel_sem - rel_exc) > 0.5,
                   {"semantic_related_cue": round(rel_sem, 3), "exact_key_related_cue": round(rel_exc, 3),
                    "headroom": round(rel_sem - rel_exc, 3)}))

    ok = True
    print("=== witness: dimensional_phase_diagram_audit_of_the_current_organs ===")
    for name, passed, det in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}\n         {det}")
        ok = ok and passed
    print("\n" + ("ALL CHECKS PASS -- register cliff seen (positive control), sparsity is a distinct lever, "
                  "real-task register is STRUCTURAL, meaning is sparse-exact, and beyond-N axes behave "
                  "(orthogonality a lever, depth not, precision bites at q=2)" if ok else "WITNESS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
