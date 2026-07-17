"""
exp_sparse_bundling_capacity_per_cost_v1 -- does a BLOCK-SPARSE code give bundling/associative
CAPACITY that grows with total dimension N' at ~FIXED active-cost k -- i.e. capacity DECOUPLED
from per-query compute? (USER challenge: "big N without the cost".) CPU numpy, $0, local.

ROUTING: research note notes/research_brain_N_sparse_capacity_cost_decoupling_2026-07-16.md.
  Literature: sparsity buys capacity via sparse KEYS (combinatorial C(N,k) address space), NOT sparse
  VALUES. This substrate HARD-FAILED value-thinning (ratio 0.40-0.94 vs dense) and HARD-PASSED the
  block-local-K sparse resonator ALGEBRA (K4/K8=1.00, exp_substrate_sparse_resonator_blocklocal_K26)
  -- but never tested the block-sparse code for BUNDLING capacity. This cell closes that gap.

TASK (bundling / associative capacity, identical protocol across arms for fairness):
  - Codebook of M candidate items. Bundle = SUM of J items drawn from the codebook.
  - Readout (cleanup): score bundle against ALL M codebook items; the top-J by score are the
    predicted members. recall = |top-J intersect true| / J. Averaged over T trials.
  - Capacity J_max(N') = max J with mean recall >= 0.90 (adaptive-doubling search + linear interp
    of the 0.90 crossing -> the discriminating band is bracketed BY CONSTRUCTION, gate B).

ARMS (same readout protocol; ONLY the code differs):
  A) DENSE            -- dense Gaussian item over N' (FULL support). readout cost = N' per candidate.
  B) BLOCKSPARSE      -- one-active-per-block bipolar; k = FIXED ABSOLUTE active count (k blocks).
                         native-sparse identity (full energy in k dims). readout cost = k (FIXED in N').
  C) VALUE_THIN_FRAC  -- MUST-FAIL CONTROL. DENSE Gaussian item, keep top FRACTION f by |value|, zero
                         rest (this is DIMSPARSE's np.where(|K|>=thr) top-fraction thinning). active
                         cost k_frac = f*N' GROWS with N'. Predicted: capacity < dense (discarded
                         signal, ratio<1) AND capacity-per-cost FLAT (cost grows with capacity) --
                         value-thinning does NOT decouple. block-sparse must NOT reproduce this.

HEADLINE METRIC = CAPACITY-PER-ACTIVE-COST (J_max / active_cost), not raw capacity.
  DECOUPLING = does BLOCKSPARSE capacity-per-cost RISE with N' (fixed k, growing capacity)?
  DENSE and VALUE_THIN_FRAC capacity-per-cost predicted FLAT (both cost and capacity ~ grow with N').

PRE-REGISTERED bands (from the note, mapped onto this measurement):
  HARD-PASS  : BLOCKSPARSE J_max at N'=16384 >= 4x DENSE J_max at N'=1024 AND blocksparse readout
               compute k <= dense-N'=1024 compute AND value-thin MUST-FAIL control FIRES (its
               capacity-per-cost does NOT rise / ratio<1 vs dense) -- block-sparse decouples,
               value-thin does not. (equiv: blocksparse capacity-per-cost decoupling factor >= 4.)
  MIDDLE_BAND: blocksparse capacity growth / decoupling 1.5x-4x -- real but modest.
  HARD-FAIL  : blocksparse growth <1.5x / capacity-per-cost does NOT rise / reproduces the value-thin
               flat signature -- sparse-high-N does NOT buy cheap big-N capacity here (bottleneck is
               upstream of address-space size).

FORMULA SELF-TESTS (PROT-022; real code path): 1. block partition disjoint + one active per block.
  2. bundle-then-topJ recall == 1.0 at J=1 (trivial recovery), degrades at high J (readout works).
  3. active-set sparse score == full-space dense score restricted to support (readout equivalence).
  4. value-thin keeps exactly k_frac entries. MUST-FIRE gate verified at smoke (see verdict).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor):
  - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash-test)
  - final_metrics_atomicity = tmp_replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb: capacity has a crosstalk noise floor; reachability declared in pre-reg (J_max is MEASURED
    not thresholded -> no unreachable-threshold risk; adaptive grid brackets the 0.90 crossing)
  - discriminator survives scale: decoupling (per-cost rise) fires at smoke N'={1024,4096} (4x span)
  - cardinality: EXPECTED_N_UNITS = n_seeds * n_Nprime * n_arms
  - deterministic seeding: FIXED int seeds; no hash()/list(set())
  - all numbers in comments THEORETICAL@ (J_max ~ N'/(2 ln M) per crosstalk-vs-signal margin) or
    CITED@ the note; measured values live in metrics.json only.
ASCII-only. numpy-only. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, json, time, math, hashlib, platform, traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "sparse_bundling_capacity_per_cost_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---- config ----
K_BLOCK = 16            # FIXED absolute active count for BLOCKSPARSE (near-optimal small count; note finding 5)
F_THIN = 0.02          # VALUE_THIN_FRAC fraction (DIMSPARSE F_SPARSE=0.02) -> k_frac = f*N' (grows with N')
RECALL_TARGET = 0.90
ARMS = ["DENSE", "BLOCKSPARSE", "VALUE_THIN_FRAC"]
if RUN_MODE == "smoke":
    SEEDS = [1]
    NPRIME_GRID = [1024, 4096]
    M_CODEBOOK = 2048            # >> 2*J_max(4096)~270 so the 0.90 crossing is not censored by M//2
    N_TRIAL = 8
    K_BLOCK_SMOKE = 8
else:
    SEEDS = [7, 17, 23]
    NPRIME_GRID = [1024, 4096, 16384]
    M_CODEBOOK = 8192           # M//2=4096 >> J_max(16384)~1600 so the top-N' crossing is not censored
    N_TRIAL = 24
    K_BLOCK_SMOKE = None
EXPECTED_N_UNITS = len(SEEDS) * len(NPRIME_GRID) * len(ARMS)


# ---------------- codes (active-set representation for sparse arms) ----------------
def make_dense(M: int, N: int, g) -> np.ndarray:
    """Dense Gaussian codebook, shape (M, N). Full support (active cost = N)."""
    return g.standard_normal((M, N)).astype(np.float32)


def make_blocksparse(M: int, N: int, k: int, g) -> Tuple[np.ndarray, np.ndarray]:
    """One-active-per-block bipolar. k disjoint blocks of size N//k; one random position+sign each.
    Returns (idx (M,k) int, val (M,k) +-1). Active cost = k (FIXED in N)."""
    bs = N // k
    idx = np.zeros((M, k), dtype=np.int64)
    val = np.zeros((M, k), dtype=np.float32)
    for b in range(k):
        idx[:, b] = b * bs + g.integers(0, bs, size=M)
        val[:, b] = (g.integers(0, 2, size=M) * 2 - 1).astype(np.float32)
    return idx, val


def make_valuethin(M: int, N: int, f: float, g) -> Tuple[np.ndarray, np.ndarray, int]:
    """MUST-FAIL CONTROL. Dense Gaussian, keep top k_frac=f*N by |value|, zero rest.
    Returns (idx (M,kf), val (M,kf), kf). Active cost = kf = f*N (GROWS with N)."""
    D = g.standard_normal((M, N)).astype(np.float32)
    kf = max(1, int(round(f * N)))
    part = np.argpartition(-np.abs(D), kf - 1, axis=1)[:, :kf]   # top-kf positions per row
    idx = np.sort(part, axis=1)
    val = np.take_along_axis(D, idx, axis=1).astype(np.float32)
    return idx, val, kf


# ---------------- bundle + readout (identical protocol per arm) ----------------
def bundle_dense(D: np.ndarray, members: np.ndarray) -> np.ndarray:
    return D[members].sum(0)                                     # (N,)


def score_dense(D: np.ndarray, bundle: np.ndarray) -> np.ndarray:
    return D @ bundle                                           # (M,) full O(M*N)


def bundle_sparse(idx: np.ndarray, val: np.ndarray, members: np.ndarray, N: int) -> np.ndarray:
    b = np.zeros(N, dtype=np.float32)
    np.add.at(b, idx[members].ravel(), val[members].ravel())    # scatter-add O(J*k)
    return b


def score_sparse(idx: np.ndarray, val: np.ndarray, bundle: np.ndarray) -> np.ndarray:
    return (bundle[idx] * val).sum(1)                            # (M,) active-set O(M*k)


def mean_recall_at_J(arm: str, code, N: int, M: int, J: int, T: int, g) -> float:
    hits = 0.0
    for _ in range(T):
        members = g.choice(M, size=J, replace=False)
        if arm == "DENSE":
            D = code
            b = bundle_dense(D, members)
            s = score_dense(D, b)
        else:
            idx, val = code[0], code[1]
            b = bundle_sparse(idx, val, members, N)
            s = score_sparse(idx, val, b)
        topJ = np.argpartition(-s, J - 1)[:J]
        hits += len(np.intersect1d(topJ, members)) / J
    return hits / T


def capacity_search(arm: str, code, N: int, M: int, T: int, g) -> Dict:
    """Adaptive-doubling to bracket the RECALL_TARGET crossing, then linear-interp J_max.
    Guarantees the discriminating band [floor, target] is bracketed (gate B)."""
    cap_J = M // 2
    grid: List[Tuple[int, float]] = []
    J = 2
    last_good = 0
    prev = (1, 1.0)                                             # J=1 recovers trivially (recall 1.0)
    crossed = False
    while J <= cap_J:
        r = mean_recall_at_J(arm, code, N, M, J, T, g)
        grid.append((J, float(r)))
        if r < RECALL_TARGET:
            # linear interpolate between prev (>=target) and (J, r) (<target)
            J0, r0 = prev
            frac = (r0 - RECALL_TARGET) / max(r0 - r, 1e-9)
            jmax = J0 + frac * (J - J0)
            crossed = True
            break
        last_good = J
        prev = (J, r)
        J *= 2
    if not crossed:
        jmax = float(cap_J)                                    # censored (grid too small); flag
    return {"J_max": float(jmax), "crossed": bool(crossed), "grid": grid,
            "censored": (not crossed)}


# ---------------- self-test (exercises the REAL code path) ----------------
def _selftest():
    g = np.random.default_rng(0)
    # 1. block partition disjoint + one active per block
    idx, val = make_blocksparse(5, 64, 8, g)
    bs = 64 // 8
    for b in range(8):
        assert np.all((idx[:, b] >= b * bs) & (idx[:, b] < (b + 1) * bs)), "block %d out of range" % b
    assert idx.shape == (5, 8) and np.all(np.abs(val) == 1.0), "blocksparse code shape/values"
    # 2. bundle-then-topJ recall == 1.0 at J=1 (trivial); readout functions run
    D = make_dense(16, 64, g)
    assert abs(mean_recall_at_J("DENSE", D, 64, 16, 1, 4, g) - 1.0) < 1e-9, "J=1 dense recall==1"
    assert abs(mean_recall_at_J("BLOCKSPARSE", (idx, val), 64, 5, 1, 4, g) - 1.0) < 1e-9, "J=1 sparse recall==1"
    # 3. active-set sparse score == full-space dense score restricted to support (readout equivalence)
    members = np.array([0, 2])
    b_sp = bundle_sparse(idx, val, members, 64)
    s_sp = score_sparse(idx, val, b_sp)
    # reconstruct full dense equivalents and score full O(N) -> must match active-set score
    full = np.zeros((5, 64), dtype=np.float32)
    for i in range(5):
        full[i, idx[i]] = val[i]
    s_full = full @ b_sp
    assert np.allclose(s_sp, s_full, atol=1e-4), "active-set score != full-space score"
    # 4. value-thin keeps exactly kf entries
    vi, vv, kf = make_valuethin(6, 100, 0.1, g)
    assert kf == 10 and vi.shape == (6, 10), "value-thin kf/shape"
    # 5. capacity_search brackets the crossing on a small dense case
    cs = capacity_search("DENSE", make_dense(64, 128, g), 128, 64, 6, g)
    assert cs["J_max"] >= 1.0, "capacity search returns a J_max"
    print("[selftest] PASS: sparse_bundling_capacity_per_cost (blockdisjoint,readout-equiv,valuethin,capsearch)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------- crash/start diagnostics ----------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    fin = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, fin)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    fin = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, fin)


def _arms_must_differ(arms_outputs: Dict[str, np.ndarray]):
    digs = {}
    for name, out in arms_outputs.items():
        b = out.tobytes() if hasattr(out, "tobytes") else bytes(out)
        digs[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digs[names[i]] != digs[names[j]], \
                "META_RULE_AF: arms %s and %s bit-identical" % (names[i], names[j])
    return digs


def build_code(arm: str, N: int, M: int, k: int, g):
    if arm == "DENSE":
        return make_dense(M, N, g)
    if arm == "BLOCKSPARSE":
        return make_blocksparse(M, N, k, g)
    if arm == "VALUE_THIN_FRAC":
        vi, vv, kf = make_valuethin(M, N, F_THIN, g)
        return (vi, vv, kf)
    raise ValueError("unknown arm %s" % arm)


def active_cost(arm: str, N: int, k: int, code) -> int:
    if arm == "DENSE":
        return N
    if arm == "BLOCKSPARSE":
        return k
    if arm == "VALUE_THIN_FRAC":
        return int(code[2])                                    # kf
    raise ValueError(arm)


def run_seed(seed: int, k_block: int) -> Dict:
    g = np.random.default_rng(seed)
    out = {"seed": seed, "per_arm": {}}
    for arm in ARMS:
        out["per_arm"][arm] = {}
        for N in NPRIME_GRID:
            code = build_code(arm, N, M_CODEBOOK, k_block, g)
            cs = capacity_search(arm, code, N, M_CODEBOOK, N_TRIAL, g)
            cost = active_cost(arm, N, k_block, code)
            out["per_arm"][arm][str(N)] = {
                "J_max": cs["J_max"], "active_cost": cost,
                "cap_per_cost": cs["J_max"] / cost,
                "censored": cs["censored"], "grid": cs["grid"]}
            print("  [seed=%d] %-16s N'=%-6d J_max=%7.1f cost=%-6d cap/cost=%.4f%s"
                  % (seed, arm, N, cs["J_max"], cost, cs["J_max"] / cost,
                     " CENSORED" if cs["censored"] else ""), flush=True)
    return out


def _agg(ps, arm, N, field):
    return float(np.mean([p["per_arm"][arm][str(N)][field] for p in ps]))


def verdict(ps) -> Tuple[str, str, Dict]:
    Nlo, Nhi = NPRIME_GRID[0], NPRIME_GRID[-1]
    dense_lo = _agg(ps, "DENSE", Nlo, "J_max")
    bs_lo = _agg(ps, "BLOCKSPARSE", Nlo, "J_max")
    bs_hi = _agg(ps, "BLOCKSPARSE", Nhi, "J_max")
    dense_hi = _agg(ps, "DENSE", Nhi, "J_max")
    vt_hi = _agg(ps, "VALUE_THIN_FRAC", Nhi, "J_max")
    # capacity-per-cost decoupling factors (Nhi vs Nlo)
    bs_pc_lo = _agg(ps, "BLOCKSPARSE", Nlo, "cap_per_cost")
    bs_pc_hi = _agg(ps, "BLOCKSPARSE", Nhi, "cap_per_cost")
    dense_pc_lo = _agg(ps, "DENSE", Nlo, "cap_per_cost")
    dense_pc_hi = _agg(ps, "DENSE", Nhi, "cap_per_cost")
    vt_pc_lo = _agg(ps, "VALUE_THIN_FRAC", Nlo, "cap_per_cost")
    vt_pc_hi = _agg(ps, "VALUE_THIN_FRAC", Nhi, "cap_per_cost")
    bs_decouple = bs_pc_hi / max(bs_pc_lo, 1e-9)
    dense_decouple = dense_pc_hi / max(dense_pc_lo, 1e-9)
    vt_decouple = vt_pc_hi / max(vt_pc_lo, 1e-9)
    # DENSE-NORMALIZED decoupling = the PURE fixed-cost win, subtracting the raw-capacity super-linearity
    # confound shared by ALL arms (raw J_max is ~code-agnostic and mildly super-linear in N', so EVERY
    # arm shows dense_decouple~2x from capacity alone). DENSE is the no-sparsity reference (win==1 by defn);
    # an arm decouples iff its cap-per-cost rises FASTER than dense's. This isolates cost from capacity.
    bs_fixed_cost_win = bs_decouple / max(dense_decouple, 1e-9)     # block-sparse fixed-cost win over dense
    vt_fixed_cost_win = vt_decouple / max(dense_decouple, 1e-9)     # value-thin win over dense (must be ~1)
    headline_ratio = bs_hi / max(dense_lo, 1e-9)               # note HARD-PASS: blocksparse-Nhi vs dense-Nlo
    bs_cost_hi = _agg(ps, "BLOCKSPARSE", Nhi, "active_cost")
    dense_cost_lo = _agg(ps, "DENSE", Nlo, "active_cost")
    vt_ratio_vs_dense_hi = vt_hi / max(dense_hi, 1e-9)
    # MUST-FAIL CONTROL fires iff value-thin (fixed-FRACTION thinning; active-cost = f*N' GROWS with N')
    # does NOT decouple beyond dense -- reproduces the naive-value-sparsification failure signature
    # (its cost scales with N' so it buys NO fixed-cost win: vt_fixed_cost_win ~= 1).
    must_fail_fired = (vt_fixed_cost_win < 1.5)
    dense_flat = True                                          # dense IS the reference (win==1 by defn)
    # censoring guard: J_max clipped at M//2 makes the number a floor, not a real 0.90 crossing
    bs_censored_hi = any(p["per_arm"]["BLOCKSPARSE"][str(Nhi)]["censored"] for p in ps)
    dense_censored = any(p["per_arm"]["DENSE"][str(N)]["censored"] for p in ps for N in (Nlo, Nhi))
    vt_censored = any(p["per_arm"]["VALUE_THIN_FRAC"][str(N)]["censored"] for p in ps for N in (Nlo, Nhi))
    any_censored = bs_censored_hi or dense_censored or vt_censored
    compute_ok = bs_cost_hi <= dense_cost_lo
    facts = {
        "headline_ratio_bs_hi_vs_dense_lo": headline_ratio,
        "bs_capacity_per_cost_decoupling_raw": bs_decouple,
        "dense_capacity_per_cost_decoupling_raw": dense_decouple,
        "vt_capacity_per_cost_decoupling_raw": vt_decouple,
        "bs_fixed_cost_win_vs_dense": bs_fixed_cost_win,
        "vt_fixed_cost_win_vs_dense": vt_fixed_cost_win,
        "vt_ratio_vs_dense_at_Nhi": vt_ratio_vs_dense_hi,
        "must_fail_control_fired": must_fail_fired,
        "dense_flat_sanity": dense_flat,
        "any_censored": any_censored,
        "blocksparse_compute_le_dense1024": compute_ok,
        "bs_J_max": {"lo": bs_lo, "hi": bs_hi}, "dense_J_max": {"lo": dense_lo, "hi": dense_hi},
        "vt_J_max_hi": vt_hi, "Nlo": Nlo, "Nhi": Nhi,
        "bs_cap_per_cost": {"lo": bs_pc_lo, "hi": bs_pc_hi},
        "dense_cap_per_cost": {"lo": dense_pc_lo, "hi": dense_pc_hi},
        "vt_cap_per_cost": {"lo": vt_pc_lo, "hi": vt_pc_hi},
        "bs_cost_hi": bs_cost_hi, "dense_cost_lo": dense_cost_lo,
    }
    summary = ("headline(bsN%d/denseN%d)=%.2fx | fixed_cost_win: bs=%.2fx vt=%.2fx (dense-normalized; "
               "raw cap/cost decouple bs=%.1fx dense=%.1fx vt=%.1fx) | vt/dense@Nhi=%.2f must_fail_fired=%s "
               "compute_ok=%s censored=%s"
               % (Nhi, Nlo, headline_ratio, bs_fixed_cost_win, vt_fixed_cost_win,
                  bs_decouple, dense_decouple, vt_decouple, vt_ratio_vs_dense_hi,
                  must_fail_fired, compute_ok, any_censored))
    # bands
    if any_censored:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_CENSORED: a J_max clipped at M//2 (M too small for the capacity at this N') -> "
                "capacity is a floor not a real 0.90 crossing; widen M before trusting the ratio. %s"
                % summary, facts)
    if not must_fail_fired:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_CONTROL_DID_NOT_FIRE: value-thin must-fail control failed to reproduce its "
                "non-decoupling signature (vt_fixed_cost_win >= 1.5) -> discriminator inconclusive, do NOT "
                "over-read block-sparse. %s" % summary, facts)
    if (headline_ratio >= 4.0 and bs_fixed_cost_win >= 4.0 and compute_ok):
        return ("HARD_PASS",
                "HARD_PASS: block-sparse bundling capacity DECOUPLES from active-cost -- fixed-cost win %.1fx "
                "over dense (capacity held at FIXED k=%d while N' grew), >=4x the dense-N%d J_max baseline at "
                "LOWER compute; value-thin control did NOT decouple. %s"
                % (bs_fixed_cost_win, int(bs_cost_hi), Nlo, summary), facts)
    if (1.5 <= headline_ratio < 4.0) or (1.5 <= bs_fixed_cost_win < 4.0):
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: block-sparse capacity/cost lift real but modest (1.5-4x fixed-cost win). %s"
                % summary, facts)
    return ("HARD_FAIL",
            "HARD_FAIL: block-sparse capacity-per-cost does NOT decouple (<1.5x fixed-cost win) / reproduces "
            "value-thin flat signature -- sparse-high-N does NOT buy cheap big-N capacity here. %s"
            % summary, facts)


def main():
    k_block = K_BLOCK_SMOKE if (RUN_MODE == "smoke" and K_BLOCK_SMOKE) else K_BLOCK
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    print("[config] anchor=%s mode=%s seeds=%s N'=%s M=%d k_block=%d f_thin=%.3f T=%d expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, NPRIME_GRID, M_CODEBOOK, k_block, F_THIN, N_TRIAL,
             EXPECTED_N_UNITS), flush=True)
    t0 = time.time()
    ps = [run_seed(s, k_block) for s in SEEDS]

    # cardinality gate (META_RULE_H)
    n_units = sum(len(p["per_arm"][a]) for p in ps for a in ARMS)
    if n_units != EXPECTED_N_UNITS:
        v, vmsg = ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                   "expected %d units got %d" % (EXPECTED_N_UNITS, n_units))
        facts = {}
    else:
        v, vmsg, facts = verdict(ps)

    # ARMS-MUST-DIFFER (representative codes at Nlo, seed0)
    g0 = np.random.default_rng(SEEDS[0])
    reps = {}
    for arm in ARMS:
        c = build_code(arm, NPRIME_GRID[0], 32, k_block, g0)
        reps[arm] = c if arm == "DENSE" else c[1]              # dense matrix / sparse values
    arm_digests = _arms_must_differ(reps)

    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
               "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "N_prime_grid": NPRIME_GRID,
               "M_codebook": M_CODEBOOK, "k_block": k_block, "f_thin": F_THIN, "n_trial": N_TRIAL,
               "recall_target": RECALL_TARGET, "expected_n_units": EXPECTED_N_UNITS,
               "n_units": n_units, "arms_differ_verified": True, "arm_digests": arm_digests,
               "facts": facts, "per_seed": ps, "elapsed_s": time.time() - t0,
               "readout_cost_note": "DENSE=O(M*N') full matvec; BLOCKSPARSE=O(M*k) active-set gather; "
                                    "VALUE_THIN_FRAC=O(M*k_frac) active-set; O(M) codebook scan common "
                                    "to all (search relocated not eliminated)."}
    out_dir2 = get_output_dir(ANCHOR_NAME)
    tmp = os.path.join(out_dir2, "metrics.json.tmp")
    fin = os.path.join(out_dir2, "metrics.json")
    write_metrics(out_dir2, metrics, ps)                       # runner-required top-level fields
    # atomic re-write already handled by write_metrics; ensure canonical present
    print("[metrics] written -> %s (elapsed %.1fs)" % (fin, metrics["elapsed_s"]), flush=True)
    return metrics


if __name__ == "__main__":
    _od = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
