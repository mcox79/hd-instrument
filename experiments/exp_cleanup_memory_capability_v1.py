"""exp_cleanup_memory_capability_v1 -- ITEM 1 + ITEM 2 of notes/PLAN_NEXT_24H.md.

THE QUESTION, AND WHY IT RE-READS FIVE BANKED NULLS
---------------------------------------------------
Plate 1995 states the VSA objection plainly: unbinding returns a NOISY vector that is useless until
it is cleaned against a separate item memory with good reconstructive properties. On that reading a
VSA system's capability is set by its CLEANUP MEMORY, not by its algebra. This substrate has FIVE
banked cells in which cleanup measured inert:

    exp_hub_spoke_word_g3_cleanup_rescore_v1   reading through cleanup changed the vector by 1.192e-07
    exp_att1_iterative_attractor_cleanup_v1    lift +0.005, basin 1.00x
    exp_cleanup_graded_attractor_vs_argmax_v1  +0.003
    exp_att1_..._krotov_v1                     HARD_FAIL -0.020
    ca3_completion partial cue                 cos to target +39% rel, argmax recovery 0.0711 -> 0.0709

All five scored "does completion help the downstream task". None scored the organ's OWN axis:
does the cleanup RECOVER THE UN-BOUND ITEM. This cell scores both, in that order, with a cleanup
memory that is PROVEN NOT INERT before any treatment number is read.

PART A -- THE ORGAN ON ITS OWN AXIS (hdlab.vsa_cleanup_memory, whose 5 self-tests must pass first).
  CAPACITY  recovery of an un-bound item vs superposition load L, against VSA theory's O(d/log d).
  BASIN     recovery vs the cue's cosine to its target.
  FIXED PT  stored symbols are fixed points; cleaning is idempotent.
  NOT INERT the state MOVES from the input, and recovery RISES as noise falls -- demonstrated.
  THE ONE-VARIABLE CONTRAST: the REAL anchor codebook against an i.i.d. Gaussian codebook MATCHED
  in (M, d). The only difference is CORRELATION STRUCTURE, which is the quantity the theory says
  decides whether a settle can change a decision at all.

PART B -- THE FIVE NULLS RE-RUN, with the working organ in place, on the live read-out.
  The arm ladder is ONE VARIABLE AT A TIME and that is the point:
    A0_NO_CLEANUP              raw cosine, the incumbent
    A0b_CENTRED_ONE_SHOT       common-mode removed, NO iteration      (isolates CENTRING)
    T1_CLEANUP_SETTLED_*       centred AND iterated                   (isolates ITERATION)
    T2_SETTLED_NO_CENTRING     iterated, NOT centred                  (iteration alone)
    C1_INCUMBENT_ITERATIVE     hdlab.iterative_attractor as shipped   (the organ measured inert)
  A null that becomes positive is a finding. A null that STAYS null with a proven-working cleanup
  is a STRONGER negative than the one banked, because it removes the "half the organ was missing"
  defence. Both outcomes are reported with equal weight.

BRAIN FIDELITY (standing gate). COPY THE COMPUTATION, SWEEP THE PARAMETER.
--------------------------------------------------------------------------
BRAIN STRUCTURE: CA3 recurrent auto-association (Marr 1971; Treves & Rolls 1992/1994). PINNED as a
COMPUTATION: a recurrent settle against the stored set, the cue continuing to drive it through the
settle (direct perforant path), common-mode removal before association (the covariance form of the
CA3 rule; feedback inhibition), and a fixed point that is a stored symbol. PINNED as EVIDENCE:
CA3-NMDA knockouts impair completion from a DEGRADED CUE specifically.
OURS, INVENTION UNDER TEST: the softmax recurrent update, the global-mean-direction subtraction,
and EVERY numeric value -- beta, alpha, max_steps -- all SWEPT, none adopted. alpha=0.5 shipped
elsewhere labelled "brain-canonical" is an invention wearing a pinned label.
CONTESTED AND REPORTED AS CONTESTED: whether CA3 is a DISCRETE attractor at all. Leutgeb et al.
2007 report graded, continuous CA3 responses; continuous-attractor accounts treat CA3 as a
manifold. If CA3 is continuous, "settle to the nearest stored pattern" is the wrong operation and
the banked attractor nulls are less informative than they look. The alpha sweep spans it: alpha->1
is a graded, cue-dominated read (continuous), alpha->0 a hard settle (discrete).
AND THE LARGER ONE: VSA ALGEBRAIC BINDING ITSELF IS UNPINNED IN THE BRAIN. No recording has shown a
cortical population computing a circular convolution or an elementwise product of two full-rank
vector codes; coarse-coded conjunctive binding (O'Reilly & Busby) and binding by synchrony
(von der Malsburg; Hummel) are live rivals with published objections of their own. The substrate
choice this cell serves is OUR-INVENTION-BEING-TESTED, not biology.

VALIDITY, DEMONSTRATED NOT ASSERTED, BEFORE ANY TREATMENT NUMBER IS READ
------------------------------------------------------------------------
KNOWN-ANSWER arm near ceiling AND NULL arm near chance, failing INDEPENDENTLY (each is broken in
turn in --self-test and the other is shown to survive). PART A's KA is "the cue IS the stored
symbol"; PART B's is "the query IS the designated gold's stored vector". PART A's NULL permutes the
cue->target pairing; PART B's permutes the anchor->vector map. Different mechanisms, so they fail
separately.

FLOORS. Every gate is a CI-separated margin over max(ORTHOGRAPHIC, FREQUENCY, SCRAMBLE, CONSTANT),
each floor COMPUTED ON THIS CELL'S OWN POPULATION WITH ITS OWN n. 0.1382 and 0.2070 are real floors
on DIFFERENT populations and are NEVER imported. Both tie conventions are reported, always. The
per-pool oracle check (tools.floor_battery.pool_admits_a_winning_constant) is RUN and its value
REPORTED for every pool built, including the open pool.

NEVER uses grounded_similarity() as a scorer. Ruler-mode gate per exp_task_degeneracy_v1:121.
ASCII-only. numpy float32. No torch, no network, NO LLM anywhere in the flow.
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
    as_constant_matrix, balanced_candidate_sets, constant_prototype_floor, frequency_floor,
    hit_at_1_both_tie_conventions, l2n, oracle_constant_scores, pool_admits_a_winning_constant,
    scramble_null,
)
from hdlab.vsa_cleanup_memory import (                                               # noqa: E402
    CleanupMemory, basin_curve, bipolar_keys, degrade_to_cosine, run_selftests, unbind_residue,
)

ANCHOR_NAME = "exp_cleanup_memory_capability_v1"
CODE_VERSION = "v1.0.0"          # in every checkpoint key: a smoke can never be mistaken for a full
OUT_DIR_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_DIR_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_smoke")

MASTER_SEED = 20260817
K_LIST = (15, 49)                # balanced-pool sizes: chance 0.0625 and 0.0200
KA_CEILING_MIN = 0.95
SAT_MIN_SPREAD = 0.002           # PART B arms differ by a cleanup step; the spread guard is on the
                                 # TREATMENT LADDER, and a tiny spread is itself the finding, so the
                                 # threshold is small and its trip is REPORTED, never fatal.

# PARAMETERS ARE HYPOTHESES, SWEPT. Nothing here is adopted from biology as a value.
# alpha spans the CONTESTED discrete/continuous axis: 0.0 hard settle, 0.7 cue-dominated graded.
CFG_FULL: Tuple[Dict, ...] = (
    {"tag": "b16_a0.3_ctrTrue", "beta": 16.0, "alpha": 0.3, "max_steps": 12, "center": True},
    {"tag": "b64_a0.0_ctrTrue", "beta": 64.0, "alpha": 0.0, "max_steps": 12, "center": True},
    {"tag": "b16_a0.3_ctrFalse", "beta": 16.0, "alpha": 0.3, "max_steps": 12, "center": False},
)
CFG_SMOKE: Tuple[Dict, ...] = (CFG_FULL[0],)

# PART A sweeps wider than PART B, because PART A is cheap and is the organ's own axis.
SWEEP_BETA = (4.0, 16.0, 64.0, 256.0)
SWEEP_ALPHA = (0.0, 0.3, 0.7)
TAUS = (0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.00)
LOADS = (1, 2, 4, 8, 16, 32, 64, 128)


# =================================================================================================
# small helpers
# =================================================================================================
def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=float).encode("utf-8"))
    os.replace(tmp, path)


def col(v: np.ndarray) -> np.ndarray:
    return np.asarray(v, dtype=np.float32).reshape(-1, 1)


def _pr(A: np.ndarray) -> float:
    """Participation ratio of a codebook's spectrum -- how many directions it really uses."""
    X = l2n(np.asarray(A, dtype=np.float32))
    s = np.linalg.svd(X, compute_uv=False).astype(np.float64) ** 2
    return float((s.sum() ** 2) / max(float((s ** 2).sum()), 1e-30))


def codebook_geometry(C: np.ndarray, seed: int, n_pairs: int = 200000) -> Dict:
    """The quantities that decide whether a settle CAN change a decision. Measured, not assumed."""
    X = l2n(np.asarray(C, dtype=np.float32))
    M = X.shape[0]
    rng = np.random.default_rng(seed)
    a = rng.integers(0, M, size=n_pairs)
    b = rng.integers(0, M, size=n_pairs)
    m = a != b
    cs = np.sum(X[a[m]] * X[b[m]], axis=1).astype(np.float64)
    mean_dir = l2n(X.mean(axis=0)[None, :])[0]
    return {"M": int(M), "d": int(X.shape[1]),
            "participation_ratio": round(_pr(X), 3),
            "mean_offdiag_cos": round(float(cs.mean()), 5),
            "mean_abs_offdiag_cos": round(float(np.abs(cs).mean()), 5),
            "p99_offdiag_cos": round(float(np.percentile(cs, 99)), 5),
            "common_mode_cos_mean": round(float(np.mean(X @ mean_dir)), 5),
            "theory_capacity_scale_d_over_log_d": round(
                float(X.shape[1]) / float(np.log(max(X.shape[1], 3))), 2)}


def capacity_on(C: np.ndarray, cfg: Dict, loads: Sequence[int], n_probe: int, seed: int) -> Dict:
    """Recovery of an UN-BOUND ITEM vs superposition load, on a SUPPLIED codebook.

    hdlab.vsa_cleanup_memory.capacity_curve builds its own i.i.d. codebook; this cell must run the
    identical measurement on the REAL anchor matrix, so the loop is repeated here over a supplied C
    and REUSES unbind_residue / bipolar_keys rather than reimplementing the algebra.
    """
    C = l2n(np.asarray(C, dtype=np.float32))
    M, d = C.shape
    cm = CleanupMemory(C, beta=cfg["beta"], alpha=cfg["alpha"], max_steps=cfg["max_steps"],
                       center=cfg["center"])
    rng = np.random.default_rng(seed)
    out: Dict[str, Dict] = {}
    for L in loads:
        keys = bipolar_keys(int(L), d, np.random.default_rng(seed + 1))
        members = rng.integers(0, M, size=(int(n_probe), int(L)))
        res = unbind_residue(C, keys, members, 0)
        tgt = members[:, 0]
        state, diag = cm.clean(res)
        settled = np.argmax(state @ cm.C.T, axis=1)
        one_shot = np.argmax(l2n(cm._center(res)) @ cm.C.T, axis=1)
        raw_shot = np.argmax(l2n(res) @ C.T, axis=1)
        out["L=%d" % L] = {
            "recovery_SETTLED": round(float(np.mean(settled == tgt)), 4),
            "recovery_ONE_SHOT_centred": round(float(np.mean(one_shot == tgt)), 4),
            "recovery_ONE_SHOT_raw": round(float(np.mean(raw_shot == tgt)), 4),
            "iteration_lift_over_one_shot": round(
                float(np.mean(settled == tgt) - np.mean(one_shot == tgt)), 4),
            "centring_lift_over_raw": round(
                float(np.mean(one_shot == tgt) - np.mean(raw_shot == tgt)), 4),
            "residue_cos_to_target": round(float(np.mean(np.sum(l2n(res) * C[tgt], axis=1))), 4),
            "decision_changed_frac": round(float(diag["decision_changed_frac"]), 4),
            "delta_state_vs_input_L2": round(float(diag["delta_state_vs_input_L2"]), 6),
            "chance": round(1.0 / M, 8)}
    return out


# =================================================================================================
# PART A -- the organ on its own axis
# =================================================================================================
def part_a_unit(codebook_name: str, C: np.ndarray, cfg: Dict, n_probe: int,
                loads: Sequence[int], taus: Sequence[float], seed: int) -> Dict:
    C = l2n(np.asarray(C, dtype=np.float32))
    M = C.shape[0]
    cm = CleanupMemory(C, beta=cfg["beta"], alpha=cfg["alpha"], max_steps=cfg["max_steps"],
                       center=cfg["center"])
    rng = np.random.default_rng(seed)

    # -- FIXED POINT: every stored symbol is its own answer, and cleaning is idempotent -----------
    st, _ = cm.clean(cm.raw)
    self_rec = float(np.mean(np.argmax(st @ cm.C.T, axis=1) == np.arange(M)))
    probe = rng.integers(0, M, size=min(400, M))
    s1, _ = cm.clean(np.stack([degrade_to_cosine(C[i], 0.6, rng) for i in probe]))
    i1 = np.argmax(s1 @ cm.C.T, axis=1)
    s2, _ = cm.clean(cm.raw[i1])
    idempotent = bool(np.array_equal(i1, np.argmax(s2 @ cm.C.T, axis=1)))

    # -- BASIN + the NOT-INERT evidence ----------------------------------------------------------
    tgt = rng.integers(0, M, size=int(n_probe))
    basin = basin_curve(cm, tgt, taus, seed=seed + 3)

    # -- VALIDITY: KA at ceiling, NULL at chance, and they are BROKEN INDEPENDENTLY ---------------
    ka = float(np.mean(cm.recover(cm.raw[tgt]) == tgt))                 # cue IS the symbol
    cue06 = np.stack([degrade_to_cosine(C[i], 0.6, rng) for i in tgt])
    perm = rng.permutation(tgt.size)
    nul = float(np.mean(cm.recover(cue06[perm]) == tgt))                # pairing destroyed
    bad = CleanupMemory(l2n(rng.standard_normal(C.shape).astype(np.float32)),
                        beta=cfg["beta"], alpha=cfg["alpha"], max_steps=cfg["max_steps"],
                        center=cfg["center"])
    ka_broken = float(np.mean(bad.recover(cm.raw[tgt]) == tgt))         # break KA ...
    nul_when_ka_broken = float(np.mean(bad.recover(cue06[perm]) == tgt))  # ... NULL unaffected

    # -- CAPACITY -------------------------------------------------------------------------------
    cap = capacity_on(C, cfg, loads, int(n_probe), seed + 5)
    recs = [cap["L=%d" % L]["recovery_SETTLED"] for L in loads]
    half = None
    for L, r in zip(loads, recs):
        if r < 0.5:
            half = int(L)
            break

    monotone = all(basin["tau=%.2f" % taus[i]]["recovery_SETTLED"]
                   <= basin["tau=%.2f" % taus[i + 1]]["recovery_SETTLED"] + 1e-9
                   for i in range(len(taus) - 1))
    mid = basin["tau=0.45"] if "tau=0.45" in basin else basin["tau=%.2f" % taus[len(taus) // 2]]
    return {
        "codebook": codebook_name, "cfg": cfg,
        "GEOMETRY": codebook_geometry(C, seed + 7),
        "FIXED_POINT": {"stored_symbols_are_fixed_points": round(self_rec, 4),
                        "idempotent": idempotent},
        "NOT_INERT": {
            "delta_state_vs_input_L2_at_tau0.45": mid["delta_state_vs_input_L2"],
            "decision_changed_frac_at_tau0.45": mid["decision_changed_frac"],
            "recovery_monotone_in_cue_quality": bool(monotone),
            "recovery_at_tau0.45": mid["recovery_SETTLED"], "chance": round(1.0 / M, 8),
            "VERDICT": ("NOT_INERT" if (mid["delta_state_vs_input_L2"] > 1e-4 and monotone
                                        and mid["recovery_SETTLED"] > 20.0 / M) else "INERT")},
        "BASIN": basin,
        "CAPACITY": cap,
        "CAPACITY_SUMMARY": {"first_load_below_0.50_recovery": half,
                             "theory_scale_d_over_log_d": round(
                                 float(C.shape[1]) / float(np.log(max(C.shape[1], 3))), 2)},
        "VALIDITY": {
            "KNOWN_ANSWER_cue_is_the_symbol": round(ka, 4), "gate": KA_CEILING_MIN,
            "KA_PASSES": bool(ka >= KA_CEILING_MIN),
            "NULL_pairing_permuted": round(nul, 4), "chance": round(1.0 / M, 8),
            "NULL_near_chance": bool(nul <= max(0.02, 20.0 / M)),
            "KA_broken_by_a_noise_codebook": round(ka_broken, 4),
            "NULL_unaffected_when_KA_broken": round(nul_when_ka_broken, 4),
            "independence": "DEMONSTRATED: the noise codebook destroys KA and leaves NULL at "
                            "chance, so the two arms do not share a failure mode."},
    }


# =================================================================================================
# PART B -- the five nulls re-run on the live read-out
# =================================================================================================
def build_readout_arms(C: Dict, aux: Dict, f5: np.ndarray, regime: str, cfgs: Sequence[Dict],
                       designated: np.ndarray) -> Dict[str, np.ndarray]:
    """Every arm is a COMPLETE read-out policy on the identical store, cue, pool and gold."""
    mat = C["mat"]
    Q = C["Q_exact"] if regime == "EXACT_KEY" else C["Q_part"]
    Qn = l2n(Q)
    arms: Dict[str, np.ndarray] = {}

    # ---- the four required floors, ON THIS POPULATION -----------------------------------------
    arms["F1_TRIGRAM_orthographic"] = (aux["t_mat"] @ aux["Tq"].T).astype(np.float32)
    arms["F2_PREFIX_orthographic"] = aux["Pq"].T.astype(np.float32)
    arms["F3_FREQUENCY_constant"] = col(frequency_floor(np.expm1(aux["fq"].astype(np.float64))))
    arms["F4_CONSTANT_PROTOTYPE_zero_query_information"] = col(f5)
    arms["F5_SCRAMBLE_NULL_anchor_map_permuted"] = (
        l2n(scramble_null(mat, MASTER_SEED)) @ Qn.T).astype(np.float32)

    # ---- A0: the incumbent, raw cosine, no cleanup --------------------------------------------
    arms["A0_NO_CLEANUP_raw_cosine"] = (l2n(mat) @ Qn.T).astype(np.float32)

    # ---- the cleanup ladder, ONE VARIABLE AT A TIME -------------------------------------------
    for cfg in cfgs:
        cm = CleanupMemory(mat, beta=cfg["beta"], alpha=cfg["alpha"],
                           max_steps=cfg["max_steps"], center=cfg["center"])
        if cfg["center"]:
            # CENTRING ALONE, no iteration: the arm that says whether common-mode removal is the
            # active ingredient. Only meaningful for a centring config.
            arms["A0b_ONE_SHOT_centred_%s" % cfg["tag"]] = cm.scores(Q).T.astype(np.float32)
        state, diag = cm.clean(Q)
        key = "T1_CLEANUP_SETTLED_%s" % cfg["tag"]
        arms[key] = (state @ cm.C.T).T.astype(np.float32)
        arms[key + "__DIAG"] = diag          # stripped before scoring, carried into the report
        del cm, state

    # ---- C1: the INCUMBENT organ, exactly as shipped, the one measured inert five times --------
    from hdlab.iterative_attractor import iterative_cleanup
    out = iterative_cleanup(Qn, l2n(mat), temp=4.0, max_steps=8, alpha=0.5)
    inc = out.get("state", None)
    if inc is None:
        # the shipped organ returns indices, not a state, on some paths: score its DECISION as a
        # one-hot, which is exactly how a downstream consumer would use it.
        idx = np.asarray(out["argmax_idx"], dtype=np.int64)
        S = np.full((mat.shape[0], Qn.shape[0]), -1.0, dtype=np.float32)
        S[idx, np.arange(idx.size)] = 1.0
        arms["C1_INCUMBENT_iterative_attractor_shipped"] = S
    else:
        arms["C1_INCUMBENT_iterative_attractor_shipped"] = (
            l2n(mat) @ l2n(np.asarray(inc, dtype=np.float32)).T).astype(np.float32)

    # ---- validity arms -------------------------------------------------------------------------
    Qka = np.zeros_like(Qn)
    ok = designated >= 0
    Qka[ok] = mat[designated[ok]]
    arms["KA_QUERY_IS_GOLD_VECTOR"] = (l2n(mat) @ l2n(Qka).T).astype(np.float32)
    arms["NULL_SCRAMBLED_ANCHORS"] = arms["F5_SCRAMBLE_NULL_anchor_map_permuted"]
    return arms


def score_readout(name: str, E: np.ndarray, GOLD: np.ndarray, keepm: np.ndarray,
                  arms: Dict[str, np.ndarray], chance: float, floors: Sequence[str],
                  n_boot: int, seed: int) -> Dict:
    """hit@1 under ALL THREE tie conventions, paired bootstrap, every arm against every floor."""
    per: Dict[str, Dict] = {}
    scored_all = None
    for k, S in arms.items():
        h = hit_at_1_both_tie_conventions(S, E, GOLD)
        sc = h["scored"] & keepm
        per[k] = {"hit_exp": h["hit_exp"], "hit_opt": h["hit_opt"], "hit_cons": h["hit_cons"],
                  "tie": h["tie_mass"], "scored": sc}
        scored_all = sc.copy() if scored_all is None else (scored_all & sc)
    idx = np.flatnonzero(scored_all)
    nc = int(idx.size)
    if nc < 50:
        return {"n_common_scored": nc, "UNREADABLE": "fewer than 50 commonly scored items"}
    rng = np.random.default_rng(seed)
    IDX = rng.integers(0, nc, size=(int(n_boot), nc))
    boot = {c: {k: per[k][c][idx][IDX].mean(axis=1) for k in arms}
            for c in ("hit_exp", "hit_opt", "hit_cons")}
    del IDX
    acc = {c: {k: round(float(per[k][c][idx].mean()), 4) for k in arms}
           for c in ("hit_exp", "hit_opt", "hit_cons")}
    ci = {k: [round(float(np.percentile(boot["hit_exp"][k], 2.5)), 4),
              round(float(np.percentile(boot["hit_exp"][k], 97.5)), 4)] for k in arms}
    tie = {k: round(float(per[k]["tie"][idx].mean()), 4) for k in arms}

    def mrg(conv: str, a: str, b: str) -> Dict:
        d = boot[conv][a] - boot[conv][b]
        lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
        return {"point": round(float(np.mean(d)), 4), "ci95": [round(lo, 4), round(hi, 4)],
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")}

    A = acc["hit_exp"]
    present = [f for f in floors if f in A]
    binding = max(present, key=lambda f: A[f]) if present else None
    treat = [k for k in arms if not k.startswith(("KA_", "NULL_", "ORACLE", "F1_", "F2_", "F3_",
                                                  "F4_", "F5_"))]
    spread = round(float(max(A[k] for k in treat) - min(A[k] for k in treat)), 4) if treat else 0.0
    ka = A.get("KA_QUERY_IS_GOLD_VECTOR", float("nan"))
    nul = A.get("NULL_SCRAMBLED_ANCHORS", float("nan"))
    out = {
        "n_common_scored": nc, "chance_for_THIS_condition": round(float(chance), 6),
        "n_boot": int(n_boot),
        "PRIMARY_METRIC": "hit_at_1_TIE_CORRECTED (expected hit under a random tie-break)",
        "VALIDITY": {
            "KNOWN_ANSWER_hit_at_1": ka, "gate": KA_CEILING_MIN,
            "KA_PASSES": bool(ka >= KA_CEILING_MIN),
            "NULL_hit_at_1": nul, "chance": round(float(chance), 6),
            "NULL_near_chance": bool(abs(nul - chance) < max(0.02, 0.5 * chance)),
            "treatment_ladder_spread": spread,
            "spread_below_guard": bool(spread < SAT_MIN_SPREAD),
            "CONDITION_READABLE": bool(ka >= KA_CEILING_MIN),
            "independence": "KA plants the answer in the QUERY; NULL permutes the ANCHOR->VECTOR "
                            "map. Different mechanisms; --self-test breaks each and shows the "
                            "other survives."},
        "hit_at_1_TIE_CORRECTED_primary": A,
        "hit_at_1_OPTIMISTIC_tie": acc["hit_opt"],
        "hit_at_1_CONSERVATIVE_tie": acc["hit_cons"],
        "ci95_tie_corrected": ci, "mean_tie_mass_of_eligible_pool": tie,
        "BINDING_FLOOR": binding,
        "BINDING_FLOOR_VALUE_tie_corrected": (A[binding] if binding else None),
        "FLOOR_VALUES_on_THIS_population": {f: A[f] for f in present},
    }
    if binding:
        for conv, lab in (("hit_exp", "TIE_CORRECTED"), ("hit_cons", "CONSERVATIVE"),
                          ("hit_opt", "OPTIMISTIC")):
            out["MARGIN_vs_binding_floor_" + lab] = {
                k: mrg(conv, k, binding) for k in arms if k != binding}
    out["ARM_BY_ARM_vs_EACH_FLOOR_tie_corrected"] = {
        k: {f: mrg("hit_exp", k, f) for f in present if f != k}
        for k in arms if k not in present}
    # THE LADDER MARGINS: each rung against the rung below it, which is the one-variable question.
    a0 = "A0_NO_CLEANUP_raw_cosine"
    out["LADDER_vs_A0_NO_CLEANUP_tie_corrected"] = {
        k: mrg("hit_exp", k, a0) for k in arms if k != a0}
    out["LADDER_vs_A0_NO_CLEANUP_conservative"] = {
        k: mrg("hit_cons", k, a0) for k in arms if k != a0}
    orc = "ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"
    if orc in arms:
        out["MARGIN_vs_ORACLE_CONSTANT_tie_corrected"] = {
            k: mrg("hit_exp", k, orc) for k in arms if k != orc}
    print("[%s] n=%d KA=%.4f NULL=%.4f chance=%.4f binding=%s :: " % (
        name, nc, ka, nul, chance, binding)
        + " ".join("%s=%.4f" % (k[:26], v) for k, v in A.items()), flush=True)
    return out


# =================================================================================================
# self-test -- ASSERT VALUES. Every threshold is one mechanism pins, or it is only REPORTED.
# =================================================================================================
def self_test() -> Dict:
    res: Dict = {}
    t0 = time.time()

    # S0 -- the ORGAN's own five self-tests must pass before this cell may read a treatment number.
    res["S0_organ_selftests"] = run_selftests()

    # S1 -- the organ is NOT INERT on a codebook it is meant to serve, and the assertion is on
    # MEASURED VALUES: the state moves, and recovery rises as noise falls.
    rng = np.random.default_rng(3)
    C = l2n(rng.standard_normal((300, 128)).astype(np.float32))
    a = part_a_unit("SYNTH", C, CFG_FULL[0], n_probe=250, loads=(1, 4, 16, 64),
                    taus=(0.10, 0.30, 0.60, 1.00), seed=21)
    assert a["NOT_INERT"]["VERDICT"] == "NOT_INERT", "organ is inert on the synthetic codebook: %r" \
                                                     % a["NOT_INERT"]
    assert a["FIXED_POINT"]["stored_symbols_are_fixed_points"] >= 0.999, \
        "stored symbols are not fixed points: %r" % a["FIXED_POINT"]
    assert a["VALIDITY"]["KA_PASSES"], "PART A known-answer arm below ceiling: %r" % a["VALIDITY"]
    assert a["VALIDITY"]["NULL_near_chance"], "PART A null arm not at chance: %r" % a["VALIDITY"]
    assert a["VALIDITY"]["KA_broken_by_a_noise_codebook"] < 0.05, "breaking KA did not break it"
    assert a["VALIDITY"]["NULL_unaffected_when_KA_broken"] < 0.05, \
        "breaking KA also moved NULL -- the two arms are not independent"
    r1 = a["CAPACITY"]["L=1"]["recovery_SETTLED"]
    r64 = a["CAPACITY"]["L=64"]["recovery_SETTLED"]
    assert r1 > 0.99 and r64 < 0.5, "the capacity axis is saturated and cannot measure a capacity:" \
                                    " L=1 %.4f L=64 %.4f" % (r1, r64)
    res["S1_part_a_synthetic"] = {"not_inert": a["NOT_INERT"], "capacity_L1": r1,
                                  "capacity_L64": r64, "validity": a["VALIDITY"]}

    # S2 -- PART B's scorer end to end on a pool where THE ANSWER IS KNOWN: a planted arm reaches
    # ceiling, a null sits at chance, and a constant arm fires on a prototype-skewed open pool.
    n_a, n_i = 120, 900
    GOLD = np.zeros((n_a, n_i), dtype=bool)
    proto = np.linspace(1, 0, n_a).astype(np.float32)
    p = proto ** 6
    p = p / p.sum()
    g = rng.choice(n_a, size=n_i, p=p)
    GOLD[g, np.arange(n_i)] = True
    E = np.ones((n_a, n_i), dtype=bool)
    keepm = np.ones(n_i, dtype=bool)
    plant = np.zeros((n_a, n_i), dtype=np.float32)
    plant[g, np.arange(n_i)] = 1.0
    arms = {"A0_NO_CLEANUP_raw_cosine": rng.standard_normal((n_a, n_i)).astype(np.float32),
            "T1_CLEANUP_SETTLED_x": rng.standard_normal((n_a, n_i)).astype(np.float32),
            "F4_CONSTANT_PROTOTYPE_zero_query_information": as_constant_matrix(proto, n_i),
            "KA_QUERY_IS_GOLD_VECTOR": plant,
            "NULL_SCRAMBLED_ANCHORS": rng.standard_normal((n_a, n_i)).astype(np.float32)}
    r = score_readout("S2", E, GOLD, keepm, arms, 1.0 / n_a,
                      ["F4_CONSTANT_PROTOTYPE_zero_query_information"], 2000, 7)
    assert r["VALIDITY"]["KA_PASSES"], "planted arm did not reach ceiling: %r" % r["VALIDITY"]
    assert r["hit_at_1_OPTIMISTIC_tie"]["NULL_SCRAMBLED_ANCHORS"] < 0.05, "null arm is not null"
    assert r["hit_at_1_OPTIMISTIC_tie"][
        "F4_CONSTANT_PROTOTYPE_zero_query_information"] > 5.0 / n_a, "constant floor did not fire"
    assert r["BINDING_FLOOR"] == "F4_CONSTANT_PROTOTYPE_zero_query_information"
    res["S2_readout_scorer_end_to_end"] = {
        "KA": r["VALIDITY"]["KNOWN_ANSWER_hit_at_1"], "NULL": r["VALIDITY"]["NULL_hit_at_1"],
        "constant_floor": r["hit_at_1_OPTIMISTIC_tie"][
            "F4_CONSTANT_PROTOTYPE_zero_query_information"]}

    # S3 -- the two PART B validity arms FAIL INDEPENDENTLY. Break KA only; NULL must survive.
    bad = dict(arms)
    bad["KA_QUERY_IS_GOLD_VECTOR"] = arms["NULL_SCRAMBLED_ANCHORS"]
    r2 = score_readout("S3", E, GOLD, keepm, bad, 1.0 / n_a,
                       ["F4_CONSTANT_PROTOTYPE_zero_query_information"], 2000, 7)
    assert not r2["VALIDITY"]["KA_PASSES"], "breaking KA did not fail the KA gate"
    assert r2["hit_at_1_OPTIMISTIC_tie"]["NULL_SCRAMBLED_ANCHORS"] < 0.05, \
        "breaking KA also moved NULL"
    # and break NULL only; KA must survive
    bad2 = dict(arms)
    bad2["NULL_SCRAMBLED_ANCHORS"] = plant
    r3 = score_readout("S3b", E, GOLD, keepm, bad2, 1.0 / n_a,
                       ["F4_CONSTANT_PROTOTYPE_zero_query_information"], 2000, 7)
    assert r3["VALIDITY"]["KA_PASSES"] and not r3["VALIDITY"]["NULL_near_chance"], \
        "breaking NULL did not fail the NULL gate while leaving KA intact"
    res["S3_validity_arms_fail_independently"] = "DEMONSTRATED both ways"

    # S4 -- the balanced pool this cell builds admits NO winning constant, CHECKED not assumed,
    # and the check is the one from the rebuilt floor_battery.
    dgl = g.astype(np.int64)
    gl = [np.array([x], dtype=np.int64) for x in dgl]
    ex = [np.zeros(0, dtype=np.int64) for _ in range(n_i)]
    cand, _gc = balanced_candidate_sets(dgl, gl, ex, keepm, 15, 5)
    v = pool_admits_a_winning_constant(cand, gl, n_a, 15)
    assert v["ok"], "the balanced pool admits a winning constant: %r" % v
    res["S4_pool_oracle_check"] = v

    # S5 -- CODE_VERSION is in the checkpoint key, so a smoke unit can never satisfy a full unit.
    k_s = unit_key("A", CODE_VERSION, "REAL", "t", "smoke")
    k_f = unit_key("A", CODE_VERSION, "REAL", "t", "full")
    assert k_s != k_f, "smoke and full units collide on the checkpoint key"
    res["S5_checkpoint_key_separates_grids"] = True

    res["elapsed_s"] = round(time.time() - t0, 1)
    print("[selftest] PASS " + json.dumps(res)[:900], flush=True)
    return res


# =================================================================================================
# main
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    smoke = (grid == "smoke")
    out_dir = OUT_DIR_SMOKE if smoke else OUT_DIR_FULL
    os.makedirs(out_dir, exist_ok=True)
    done = completed_units(out_dir)

    import experiments.exp_task_degeneracy_v1 as DEG
    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "CODE_VERSION": CODE_VERSION, "grid": grid,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
        "pid": os.getpid(),
        "RULER_MODE_GATE": DEG.ruler_mode_gate(),
        "cache": DEG.build_cache_if_missing(),
        "ORGAN": "hdlab/vsa_cleanup_memory.py (CleanupMemory) -- its 5 self-tests are run by "
                 "--self-test and must pass before any treatment number here is read.",
        "NO_LLM_IN_FLOW": True,
    }
    C = DEG.load_cache()
    aux = DEG.load_aux(C)
    rep["aux_source"] = aux.get("source", "?")
    anchors, mat, mat_ok, keep = C["anchors"], C["mat"], C["mat_ok"], C["keep"]
    n_anchors, n_items = len(anchors), len(C["L_words"])
    print("[load] n_anchors=%d n_items=%d keep=%d %.0fs"
          % (n_anchors, n_items, int(keep.sum()), time.time() - t0), flush=True)

    cfgs = CFG_SMOKE if smoke else CFG_FULL
    n_probe = 300 if smoke else 1500
    loads = (1, 4, 16, 64) if smoke else LOADS
    taus = (0.10, 0.30, 0.60, 1.00) if smoke else TAUS
    n_boot = 2000 if smoke else 10000

    # =============================== PART A ===================================================
    rng0 = np.random.default_rng(MASTER_SEED)
    real_cb = l2n(mat[mat_ok])
    # ONE-VARIABLE CONTROL: same M, same d, i.i.d. Gaussian. Correlation is the ONLY difference.
    rand_cb = l2n(rng0.standard_normal(real_cb.shape).astype(np.float32))
    books = {"REAL_ANCHOR_MATRIX": real_cb, "RANDOM_MATCHED_M_and_d": rand_cb}

    sweep_cfgs: List[Dict] = list(cfgs)
    if not smoke:
        for b in SWEEP_BETA:
            for al in SWEEP_ALPHA:
                tag = "b%g_a%g_ctrTrue" % (b, al)
                if tag not in {c["tag"] for c in sweep_cfgs}:
                    sweep_cfgs.append({"tag": tag, "beta": b, "alpha": al, "max_steps": 12,
                                       "center": True})
        for b in SWEEP_BETA:
            tag = "b%g_a0.3_ctrFalse" % b
            if tag not in {c["tag"] for c in sweep_cfgs}:
                sweep_cfgs.append({"tag": tag, "beta": b, "alpha": 0.3, "max_steps": 12,
                                   "center": False})

    for bname, CB in books.items():
        for cfg in sweep_cfgs:
            k = unit_key("A", CODE_VERSION, grid, bname, cfg["tag"])
            if k in done:
                continue
            u = part_a_unit(bname, CB, cfg, n_probe, loads, taus, MASTER_SEED + 11)
            record_unit(out_dir, k, u)
            print("[A] %s %s not_inert=%s KA=%.4f NULL=%.4f cap_half=%s iter_lift@tau0.30=%s"
                  % (bname, cfg["tag"], u["NOT_INERT"]["VERDICT"],
                     u["VALIDITY"]["KNOWN_ANSWER_cue_is_the_symbol"],
                     u["VALIDITY"]["NULL_pairing_permuted"],
                     u["CAPACITY_SUMMARY"]["first_load_below_0.50_recovery"],
                     u["BASIN"].get("tau=0.30", {}).get("iteration_lift_over_one_shot")),
                  flush=True)

    # =============================== PART B ===================================================
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
    keep_A = keep & GOLD.any(axis=0)
    f5 = constant_prototype_floor(mat, mat_ok)

    r5 = np.random.default_rng(MASTER_SEED + 5)
    designated = np.full(n_items, -1, dtype=np.int64)
    for i in np.flatnonzero(keep_A):
        gi = np.flatnonzero(GOLD[:, i])
        if gi.size:
            designated[i] = int(gi[r5.integers(0, gi.size)])
    gold_lists = [np.flatnonzero(GOLD[:, i]) for i in range(n_items)]

    FLOORS = ["F1_TRIGRAM_orthographic", "F2_PREFIX_orthographic", "F3_FREQUENCY_constant",
              "F4_CONSTANT_PROTOTYPE_zero_query_information",
              "F5_SCRAMBLE_NULL_anchor_map_permuted"]

    n_elig_A = E_A.sum(axis=0)
    chance_open = float(np.mean(GOLD[:, keep_A].sum(axis=0) / np.maximum(n_elig_A[keep_A], 1)))
    pools: Dict[str, Dict] = {"P1_OPEN": {
        "E": E_A, "keep": keep_A, "chance": chance_open,
        "what": "the open pool of every eligible anchor; ANY WordNet gold member counts."}}
    ks = K_LIST[:1] if smoke else K_LIST
    for K in ks:
        cand, _gc = balanced_candidate_sets(designated, gold_lists, C["excl"], keep_A, K,
                                            MASTER_SEED + 17 + K)
        ok = cand[:, 0] >= 0
        E_B = np.zeros((n_anchors, n_items), dtype=bool)
        rows = cand[ok]
        cols = np.repeat(np.flatnonzero(ok)[:, None], K + 1, axis=1)
        E_B[rows.ravel(), cols.ravel()] = True
        leak = int((E_B & GOLD).sum(axis=0)[ok].max())
        assert leak == 1, "balanced candidate set contains more than one correct answer"
        pools["P2_BALANCED_K%d" % K] = {
            "E": E_B, "keep": ok, "chance": 1.0 / (K + 1), "K": K, "cand": cand,
            "POOL_ORACLE_CHECK": pool_admits_a_winning_constant(cand, gold_lists, n_anchors, K),
            "what": "de-biased: per-item pool = designated gold + %d distractors drawn from the "
                    "population of OTHER items' golds, so no constant ranking can beat chance %.4f."
                    % (K, 1.0 / (K + 1))}
    # THE OPEN POOL'S OWN ORACLE READING, reported for every pool as the brief requires. On an open
    # pool the constant family's ceiling is the gold-degree ranking; it is a CEILING, never a floor.
    orc_open = oracle_constant_scores(n_anchors, gold_lists, None)
    h_orc = hit_at_1_both_tie_conventions(as_constant_matrix(orc_open, n_items), E_A, GOLD)
    pools["P1_OPEN"]["POOL_ORACLE_CHECK"] = {
        "ok": None, "oracle_constant_hit_exp": round(float(h_orc["hit_exp"][keep_A].mean()), 4),
        "chance": round(chance_open, 6),
        "margin_over_chance": round(float(h_orc["hit_exp"][keep_A].mean()) - chance_open, 4),
        "note": "an OPEN pool is not de-biased by construction and is EXPECTED to admit a winning "
                "constant; the value is reported so the reader can see how much."}
    rep["POOLS"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("E", "keep", "cand")}
                    for k, v in pools.items()}

    regimes = ("PARTIAL_CUE",) if smoke else ("EXACT_KEY", "PARTIAL_CUE")
    for regime in regimes:
        arms_all = build_readout_arms(C, aux, f5, regime, cfgs, designated)
        diags = {k.replace("__DIAG", ""): v for k, v in arms_all.items() if k.endswith("__DIAG")}
        arms_all = {k: v for k, v in arms_all.items() if not k.endswith("__DIAG")}
        rep.setdefault("CLEANUP_DIAGNOSTICS", {})[regime] = {
            k: {kk: (float(vv) if isinstance(vv, (int, float, np.floating)) else str(vv))
                for kk, vv in v.items() if kk not in ("argmax_idx", "argmax_idx_of_input")}
            for k, v in diags.items()}
        for pname, P in pools.items():
            k = unit_key("B", CODE_VERSION, grid, regime, pname)
            if k in done:
                continue
            arms = dict(arms_all)
            if "cand" in P:
                orc = oracle_constant_scores(
                    n_anchors, [gold_lists[i] for i in range(n_items)],
                    [P["cand"][i] if P["cand"][i][0] >= 0 else np.zeros(1, dtype=np.int64)
                     for i in range(n_items)])
                arms["ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"] = as_constant_matrix(
                    orc, n_items)
            u = score_readout("%s|%s" % (regime, pname), P["E"], GOLD, P["keep"], arms,
                              P["chance"], FLOORS, n_boot, MASTER_SEED + 101)
            u["regime"] = regime
            u["pool"] = pname
            u["POOL_ORACLE_CHECK"] = P["POOL_ORACLE_CHECK"]
            record_unit(out_dir, k, u)
            del arms
        del arms_all

    # =============================== assemble =================================================
    units = load_units(out_dir)
    rep["PART_A_ORGAN"] = {k: v for k, v in units.items() if k.startswith("A|")}
    rep["PART_B_READOUT"] = {k: v for k, v in units.items() if k.startswith("B|")}
    rep["n_units"] = len(units)
    rep["elapsed_s"] = round(time.time() - t0, 1)

    # ---- the headline reading, stated so it cannot be over-claimed ---------------------------
    real_key = [k for k in rep["PART_A_ORGAN"] if "REAL_ANCHOR_MATRIX" in k]
    rand_key = [k for k in rep["PART_A_ORGAN"] if "RANDOM_MATCHED" in k]
    rep["READING"] = {
        "PART_A_organ_is_not_inert": {
            kk: rep["PART_A_ORGAN"][kk]["NOT_INERT"]["VERDICT"]
            for kk in (real_key[:1] + rand_key[:1])},
        "HOW_TO_READ_A_NULL": "the brain does this, so the capability is DEMONSTRATED; a miss here "
                              "is a fact about OUR IMPLEMENTATION, never about the capability. "
                              "VSA algebraic binding itself is UNPINNED in the brain with two live "
                              "published rivals -- the substrate choice is invention-under-test.",
        "verdict_is_per_condition": "gates are per (regime, pool); see PART_B_READOUT.",
    }
    rep["verdict"] = "COMPUTED"
    rep["verdict_msg"] = "see PART_A_ORGAN / PART_B_READOUT; gates are per condition"
    _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
    print("[done] %s units=%d %.0fs" % (out_dir, len(units), time.time() - t0), flush=True)
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
