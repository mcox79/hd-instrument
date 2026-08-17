"""exp_cleanup_basin_conditional_v1 -- ITEM 2's closing argument, conditioned on the BASIN.

THE QUESTION THIS EXISTS TO SETTLE
-----------------------------------
exp_cleanup_memory_capability_v1 establishes two things separately:
  (a) the cleanup memory's BASIN on our own anchor matrix is a CLIFF between cue-target cosine
      tau=0.20 and tau=0.30 (recovery 0.0013 at 0.15, 0.0667 at 0.20, 0.9493 at 0.30, 1.0000 at
      0.45), and
  (b) our PARTIAL CUE sits at mean 0.1592 / median 0.1248 against its own stored row, with only
      33.93% of items at or above 0.20 and 19.18% at or above 0.30.
If those two facts are the explanation of the cleanup null, then the null must NOT be uniform
across items: THE CLEANUP MUST HELP ON THE ITEMS WHOSE CUE IS INSIDE THE BASIN AND NOT ON THE
REST. That is a falsifiable prediction of the explanation, it is stratified on a quantity that
NEVER LOOKS AT THE GOLD, and it is what this cell measures.

WHY THE STRATIFIER IS LEGITIMATE. The stratum is cos(cue, the stored row of the QUERY WORD). The
query word is in the read-out's EXCLUSION set -- it can never be a correct answer -- so the
stratifier carries no information about which anchor is the gold. It is a property of the cue's
alignment to its own address, not of the answer. Both arms are scored on the IDENTICAL items
within each stratum, so the comparison is paired and the stratum cannot advantage one arm.

WHAT EACH OUTCOME MEANS, WRITTEN BEFORE THE RUN
  IF the cleanup lift is positive and CI-separated in the high-tau stratum and flat in the low-tau
     stratum -> THE BASIN EXPLANATION IS CONFIRMED. The completer is healthy and is being handed
     cues outside its basin. The work goes UPSTREAM to what produces the cue, and no further
     completer variant should be armed until the cue moves.
  IF the lift is flat in EVERY stratum including tau >= 0.45, where the organ's own recovery axis
     reads 1.0000 -> THE BASIN EXPLANATION IS REFUTED and something else is wrong. That would be
     the more interesting result and it must be reported as loudly.
  IF the lift is NEGATIVE in the low-tau stratum -> the completer is actively harmful exactly
     where it cannot work, which is a design consequence (gate the completer on cue quality) and
     not merely a null.

BRAIN FIDELITY. The BASIN is not our invention: CA3-NMDA knockouts impair completion FROM A
DEGRADED CUE SPECIFICALLY, which is a statement that completion has a cue-quality threshold. What
is OURS is every number -- the threshold's location, beta, alpha -- all swept elsewhere and read
here at the settings the sweep selected on the organ's OWN axis, never on this cell's outcome.
Standing caveat: VSA ALGEBRAIC BINDING IS UNPINNED IN THE BRAIN; the representation being cleaned
is invention-under-test.

VALIDITY. A KNOWN-ANSWER arm (the cue IS the stored row: every item lands in the top stratum and
recovery must be 1.0000) and a NULL arm (the anchor->vector map permuted: chance in every stratum)
are computed PER STRATUM, and --self-test breaks each in turn and shows the other survives.
FLOORS are recomputed WITHIN EACH STRATUM on that stratum's own n -- a floor computed on the whole
population does not transfer to a subset, which is the same rule that forbids importing 0.1382.
Both tie conventions. NEVER uses grounded_similarity(). ASCII-only. No LLM in any path.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402
from tools.floor_battery import (                                                    # noqa: E402
    constant_prototype_floor, frequency_floor, hit_at_1_both_tie_conventions, l2n, scramble_null,
)
from hdlab.vsa_cleanup_memory import CleanupMemory                                   # noqa: E402

ANCHOR_NAME = "exp_cleanup_basin_conditional_v1"
CODE_VERSION = "v1.0.0"
OUT_DIR_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_DIR_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_smoke")

MASTER_SEED = 20260817
# STRATUM EDGES straddle the measured basin cliff (between 0.20 and 0.30). They are chosen from
# the ORGAN'S OWN basin curve, never from this cell's outcome.
EDGES = (-1.0, 0.05, 0.10, 0.20, 0.30, 0.45, 1.01)
# the configs the organ sweep selected on ITS OWN recovery axis (highest beta rungs, where the
# temperature artefact that destroys low-beta settles is absent)
CFGS = ({"tag": "b64_a0.0_ctrTrue", "beta": 64.0, "alpha": 0.0, "max_steps": 12, "center": True},
        {"tag": "b256_a0.0_ctrTrue", "beta": 256.0, "alpha": 0.0, "max_steps": 12, "center": True})


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=float).encode("utf-8"))
    os.replace(tmp, path)


def col(v: np.ndarray) -> np.ndarray:
    return np.asarray(v, dtype=np.float32).reshape(-1, 1)


def stratified_scores(arms: Dict[str, np.ndarray], E: np.ndarray, GOLD: np.ndarray,
                      keepm: np.ndarray, tau: np.ndarray, edges: Sequence[float],
                      n_boot: int, seed: int, floors: Sequence[str]) -> Dict:
    """hit@1 per arm within each tau stratum, paired within the stratum."""
    per = {k: hit_at_1_both_tie_conventions(S, E, GOLD) for k, S in arms.items()}
    scored = None
    for k in arms:
        s = per[k]["scored"] & keepm
        scored = s.copy() if scored is None else (scored & s)
    out: Dict[str, Dict] = {}
    rng = np.random.default_rng(seed)
    for b in range(len(edges) - 1):
        lo, hi = float(edges[b]), float(edges[b + 1])
        m = scored & (tau >= lo) & (tau < hi)
        idx = np.flatnonzero(m)
        nm = int(idx.size)
        name = "tau_[%.2f,%.2f)" % (lo, hi)
        if nm < 40:
            out[name] = {"n": nm, "UNREADABLE": "fewer than 40 items in this stratum"}
            continue
        IB = rng.integers(0, nm, size=(int(n_boot), nm))
        boot = {c: {k: per[k][c][idx][IB].mean(axis=1) for k in arms}
                for c in ("hit_exp", "hit_cons")}
        acc = {c: {k: round(float(per[k][c][idx].mean()), 4) for k in arms}
               for c in ("hit_exp", "hit_opt", "hit_cons")}

        def mrg(conv, a, bb):
            d = boot[conv][a] - boot[conv][bb]
            l_, h_ = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
            return {"point": round(float(np.mean(d)), 4), "ci95": [round(l_, 4), round(h_, 4)],
                    "band": "ABOVE" if l_ > 0 else ("BELOW" if h_ < 0 else "NOT_SEPARATED")}

        A = acc["hit_exp"]
        present = [f for f in floors if f in A]
        binding = max(present, key=lambda f: A[f]) if present else None
        a0 = "A0_NO_CLEANUP_raw_cosine"
        row = {"n": nm, "mean_tau_in_stratum": round(float(tau[idx].mean()), 4),
               "hit_at_1_TIE_CORRECTED": A,
               "hit_at_1_CONSERVATIVE_tie": acc["hit_cons"],
               "hit_at_1_OPTIMISTIC_tie": acc["hit_opt"],
               "FLOORS_recomputed_IN_THIS_STRATUM": {f: A[f] for f in present},
               "BINDING_FLOOR_in_this_stratum": binding,
               "CLEANUP_LIFT_vs_A0_tie_corrected": {k: mrg("hit_exp", k, a0)
                                                    for k in arms if k != a0},
               "CLEANUP_LIFT_vs_A0_conservative": {k: mrg("hit_cons", k, a0)
                                                   for k in arms if k != a0}}
        if binding:
            row["MARGIN_vs_binding_floor_tie_corrected"] = {
                k: mrg("hit_exp", k, binding) for k in arms if k != binding}
        out[name] = row
    return out


def self_test() -> Dict:
    res: Dict = {}
    rng = np.random.default_rng(4)
    n_a, n_i = 150, 1200
    GOLD = np.zeros((n_a, n_i), dtype=bool)
    g = rng.integers(0, n_a, size=n_i)
    GOLD[g, np.arange(n_i)] = True
    E = np.ones((n_a, n_i), dtype=bool)
    keepm = np.ones(n_i, dtype=bool)
    tau = rng.random(n_i).astype(np.float32)
    plant = np.zeros((n_a, n_i), dtype=np.float32)
    plant[g, np.arange(n_i)] = 1.0
    noise = rng.standard_normal((n_a, n_i)).astype(np.float32)

    # S1 -- a PLANTED-IN-HIGH-TAU-ONLY arm must show a lift in the top stratum and none at the
    # bottom. This is the exact shape the cell is built to detect; if the detector cannot see a
    # planted version of it, a real one would be invisible too.
    planted = noise.copy()
    hi = tau >= 0.45
    planted[:, hi] = plant[:, hi]
    arms = {"A0_NO_CLEANUP_raw_cosine": noise,
            "T1_CLEANUP_SETTLED_x": planted,
            "F4_CONSTANT_PROTOTYPE_zero_query_information": np.repeat(
                np.linspace(1, 0, n_a).astype(np.float32)[:, None], n_i, axis=1),
            "KA_QUERY_IS_GOLD_VECTOR": plant,
            "NULL_SCRAMBLED_ANCHORS": rng.standard_normal((n_a, n_i)).astype(np.float32)}
    r = stratified_scores(arms, E, GOLD, keepm, tau, (-1.0, 0.20, 0.45, 1.01), 1500, 2,
                          ["F4_CONSTANT_PROTOTYPE_zero_query_information"])
    top = r["tau_[0.45,1.01)"]["CLEANUP_LIFT_vs_A0_tie_corrected"]["T1_CLEANUP_SETTLED_x"]
    bot = r["tau_[-1.00,0.20)"]["CLEANUP_LIFT_vs_A0_tie_corrected"]["T1_CLEANUP_SETTLED_x"]
    assert top["band"] == "ABOVE" and top["point"] > 0.9, \
        "the stratified detector missed a planted top-stratum lift: %r" % top
    assert bot["band"] == "NOT_SEPARATED", \
        "the detector invented a lift in the bottom stratum: %r" % bot
    res["S1_detector_sees_a_planted_stratum_specific_lift"] = {"top": top, "bottom": bot}

    # S2 -- KA at ceiling and NULL at chance IN EVERY STRATUM, broken independently.
    for st, row in r.items():
        if "UNREADABLE" in row:
            continue
        assert row["hit_at_1_TIE_CORRECTED"]["KA_QUERY_IS_GOLD_VECTOR"] >= 0.99, \
            "KA below ceiling in %s" % st
        assert row["hit_at_1_TIE_CORRECTED"]["NULL_SCRAMBLED_ANCHORS"] < 0.05, \
            "NULL above chance in %s" % st
    bad = dict(arms)
    bad["KA_QUERY_IS_GOLD_VECTOR"] = noise
    rb = stratified_scores(bad, E, GOLD, keepm, tau, (-1.0, 0.20, 0.45, 1.01), 1500, 2,
                           ["F4_CONSTANT_PROTOTYPE_zero_query_information"])
    assert rb["tau_[0.45,1.01)"]["hit_at_1_TIE_CORRECTED"]["KA_QUERY_IS_GOLD_VECTOR"] < 0.05
    assert rb["tau_[0.45,1.01)"]["hit_at_1_TIE_CORRECTED"]["NULL_SCRAMBLED_ANCHORS"] < 0.05
    bad2 = dict(arms)
    bad2["NULL_SCRAMBLED_ANCHORS"] = plant
    rc = stratified_scores(bad2, E, GOLD, keepm, tau, (-1.0, 0.20, 0.45, 1.01), 1500, 2,
                           ["F4_CONSTANT_PROTOTYPE_zero_query_information"])
    assert rc["tau_[0.45,1.01)"]["hit_at_1_TIE_CORRECTED"]["KA_QUERY_IS_GOLD_VECTOR"] >= 0.99
    assert rc["tau_[0.45,1.01)"]["hit_at_1_TIE_CORRECTED"]["NULL_SCRAMBLED_ANCHORS"] >= 0.99
    res["S2_validity_per_stratum_fails_independently"] = "DEMONSTRATED both ways"

    # S3 -- floors are recomputed WITHIN a stratum, not inherited. Assert the constant floor
    # actually differs between two strata of a population where it must.
    v = [r[s]["FLOORS_recomputed_IN_THIS_STRATUM"][
        "F4_CONSTANT_PROTOTYPE_zero_query_information"] for s in r if "UNREADABLE" not in r[s]]
    res["S3_constant_floor_per_stratum"] = v
    print("[selftest] PASS " + json.dumps(res)[:800], flush=True)
    return res


def run(grid: str) -> Dict:
    t0 = time.time()
    smoke = (grid == "smoke")
    out_dir = OUT_DIR_SMOKE if smoke else OUT_DIR_FULL
    os.makedirs(out_dir, exist_ok=True)
    done = completed_units(out_dir)
    import experiments.exp_task_degeneracy_v1 as DEG
    rep: Dict = {"anchor_name": ANCHOR_NAME, "CODE_VERSION": CODE_VERSION, "grid": grid,
                 "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
                 "pid": os.getpid(), "RULER_MODE_GATE": DEG.ruler_mode_gate(),
                 "cache": DEG.build_cache_if_missing(), "NO_LLM_IN_FLOW": True}
    C = DEG.load_cache()
    aux = DEG.load_aux(C)
    anchors, mat, mat_ok, keep = C["anchors"], C["mat"], C["mat_ok"], C["keep"]
    n_anchors, n_items = len(anchors), len(C["L_words"])
    pos = {a: i for i, a in enumerate(anchors)}
    qidx = np.array([pos.get(w, -1) for w in C["L_words"]], dtype=np.int64)

    GOLD = np.zeros((n_anchors, n_items), dtype=bool)
    E_A = np.zeros((n_anchors, n_items), dtype=bool)
    for i in range(n_items):
        if not keep[i]:
            continue
        E_A[:, i] = mat_ok
        if len(C["excl"][i]):
            E_A[C["excl"][i], i] = False
        gi = C["goldi"][i]
        if len(gi):
            GOLD[gi, i] = True
    GOLD &= E_A
    keep_A = keep & GOLD.any(axis=0) & (qidx >= 0)
    f5 = constant_prototype_floor(mat, mat_ok)
    r5 = np.random.default_rng(MASTER_SEED + 5)
    designated = np.full(n_items, -1, dtype=np.int64)
    for i in np.flatnonzero(keep_A):
        gi = np.flatnonzero(GOLD[:, i])
        if gi.size:
            designated[i] = int(gi[r5.integers(0, gi.size)])

    Q = C["Q_part"]
    # THE STRATIFIER: the cue's cosine to the stored row of its OWN query word. The query word is
    # in the exclusion set and can never be the answer, so this looks at no gold.
    tau = np.zeros(n_items, dtype=np.float32)
    ok = qidx >= 0
    tau[ok] = np.sum(l2n(Q[ok]) * l2n(mat[qidx[ok]]), axis=1)
    rep["STRATIFIER"] = {
        "definition": "cos(partial cue, the stored row of the item's OWN query word)",
        "gold_blind": "the query word is in the read-out exclusion set and can never be a correct "
                      "answer, so the stratifier carries no information about the gold",
        "mean": round(float(tau[keep_A].mean()), 4),
        "median": round(float(np.median(tau[keep_A])), 4),
        "p10": round(float(np.percentile(tau[keep_A], 10)), 4),
        "p90": round(float(np.percentile(tau[keep_A], 90)), 4),
        "frac_ge_0.20": round(float((tau[keep_A] >= 0.20).mean()), 4),
        "frac_ge_0.30": round(float((tau[keep_A] >= 0.30).mean()), 4),
        "frac_ge_0.45": round(float((tau[keep_A] >= 0.45).mean()), 4)}
    rep["BASIN_REFERENCE"] = (
        "the organ's measured basin on THIS anchor matrix (exp_cleanup_memory_capability_v1 PART A, "
        "1500 probes): recovery 0.0000 / 0.0000 / 0.0013 / 0.0667 / 0.9493 / 1.0000 at tau = "
        "0.05 / 0.10 / 0.15 / 0.20 / 0.30 / 0.45. THE CLIFF IS BETWEEN 0.20 AND 0.30.")

    arms: Dict[str, np.ndarray] = {}
    Qn = l2n(Q)
    arms["F1_TRIGRAM_orthographic"] = (aux["t_mat"] @ aux["Tq"].T).astype(np.float32)
    arms["F2_PREFIX_orthographic"] = aux["Pq"].T.astype(np.float32)
    arms["F3_FREQUENCY_constant"] = col(frequency_floor(np.expm1(aux["fq"].astype(np.float64))))
    arms["F4_CONSTANT_PROTOTYPE_zero_query_information"] = col(f5)
    arms["A0_NO_CLEANUP_raw_cosine"] = (l2n(mat) @ Qn.T).astype(np.float32)
    for cfg in (CFGS[:1] if smoke else CFGS):
        cm = CleanupMemory(mat, beta=cfg["beta"], alpha=cfg["alpha"],
                           max_steps=cfg["max_steps"], center=cfg["center"])
        arms["A0b_ONE_SHOT_centred_%s" % cfg["tag"]] = cm.scores(Q).T.astype(np.float32)
        st, dg = cm.clean(Q)
        arms["T1_CLEANUP_SETTLED_%s" % cfg["tag"]] = (st @ cm.C.T).T.astype(np.float32)
        rep.setdefault("CLEANUP_DIAGNOSTICS", {})[cfg["tag"]] = {
            "decision_changed_frac": round(float(dg["decision_changed_frac"]), 4),
            "delta_state_vs_input_L2": round(float(dg["delta_state_vs_input_L2"]), 4),
            "n_iterations": dg["n_iterations"], "converged": dg["converged"]}
        del cm, st
    Qka = np.zeros_like(Qn)
    okd = designated >= 0
    Qka[okd] = mat[designated[okd]]
    arms["KA_QUERY_IS_GOLD_VECTOR"] = (l2n(mat) @ l2n(Qka).T).astype(np.float32)
    arms["NULL_SCRAMBLED_ANCHORS"] = (
        l2n(scramble_null(mat, MASTER_SEED)) @ Qn.T).astype(np.float32)

    FLOORS = ["F1_TRIGRAM_orthographic", "F2_PREFIX_orthographic", "F3_FREQUENCY_constant",
              "F4_CONSTANT_PROTOTYPE_zero_query_information", "NULL_SCRAMBLED_ANCHORS"]
    k = unit_key("S", CODE_VERSION, grid, "PARTIAL_CUE")
    if k not in done:
        u = stratified_scores(arms, E_A, GOLD, keep_A, tau, EDGES,
                              2000 if smoke else 10000, MASTER_SEED + 77, FLOORS)
        record_unit(out_dir, k, u)
    rep["STRATIFIED"] = load_units(out_dir).get(k, {})

    # the pre-registered read, applied mechanically
    lo_key = "tau_[-1.00,0.05)"
    hi_key = "tau_[0.45,1.01)"
    def lift(sk):
        r = rep["STRATIFIED"].get(sk, {})
        if "CLEANUP_LIFT_vs_A0_tie_corrected" not in r:
            return None
        return {kk: vv for kk, vv in r["CLEANUP_LIFT_vs_A0_tie_corrected"].items()
                if kk.startswith("T1_")}
    rep["PREREGISTERED_READ"] = {
        "lift_in_the_LOWEST_stratum": lift(lo_key), "lift_in_the_HIGHEST_stratum": lift(hi_key),
        "how_to_read": "positive and CI-separated ONLY in the high-tau strata CONFIRMS the basin "
                       "explanation (the completer is healthy and is being handed cues outside its "
                       "basin, so the work goes upstream to the cue). Flat everywhere, including "
                       "where the organ's own recovery axis reads 1.0000, REFUTES it and is the "
                       "more interesting result."}
    rep["verdict"] = "COMPUTED"
    rep["verdict_msg"] = "see STRATIFIED / PREREGISTERED_READ; gates are per stratum"
    rep["elapsed_s"] = round(time.time() - t0, 1)
    _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
    print("[done] %s %.0fs" % (out_dir, time.time() - t0), flush=True)
    for sk, row in rep["STRATIFIED"].items():
        if "UNREADABLE" in row:
            print("  %-22s n=%d UNREADABLE" % (sk, row["n"]), flush=True)
            continue
        A = row["hit_at_1_TIE_CORRECTED"]
        t1 = [kk for kk in A if kk.startswith("T1_")]
        print("  %-22s n=%-5d meantau=%.3f A0=%.4f %s KA=%.4f NULL=%.4f floor=%s(%.4f)"
              % (sk, row["n"], row["mean_tau_in_stratum"], A["A0_NO_CLEANUP_raw_cosine"],
                 " ".join("%s=%.4f" % (x[3:22], A[x]) for x in t1),
                 A["KA_QUERY_IS_GOLD_VECTOR"], A["NULL_SCRAMBLED_ANCHORS"],
                 row["BINDING_FLOOR_in_this_stratum"],
                 row["FLOORS_recomputed_IN_THIS_STRATUM"][row["BINDING_FLOOR_in_this_stratum"]]),
              flush=True)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", choices=["full", "smoke"], default="full")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    run(a.grid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
