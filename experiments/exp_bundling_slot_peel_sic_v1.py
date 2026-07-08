"""
exp_bundling_slot_peel_sic_v1.py -- THE lever for the two-head additive-bundling capacity wall.

RESEARCH CONTEXT (drill notes/research_bundling_capacity_beyond_fixed_N_theta_gamma_chunking_sparse_2026-07-08.md):
  Two-head encoder superposition-recall degrades with bundle size J (flat additive superposition:
  graceful decay observed in the real encoder). The drill's brain-grounded hypothesis (Lisman-Idiart
  theta-gamma nested slots + SIC/SPARC sequential cancellation) predicts: theta-gamma SLOTTING alone
  will NOT raise bundling capacity; slotting PLUS sequential cancellation (peel/deflate) WILL.

WHAT THIS CELL TESTS (5 arms, PAIRED per trial from a shared vocabulary codebook + shared true item set):
  Two encodings per trial:
    Encoding A (FLAT sum):  Sf = sum_j book[item_j]                       (unkeyed superposition)
    Encoding B (SLOT sum):  Ss = sum_j slot_j (*) book[item_j]            (theta-gamma phase-slotted)
  Arms:
    1. FLAT_TOPJ       -- Encoding A, cleanup vs full vocab, take top-J (strongest fair flat readout).
                          The frontier/negative control that degrades as J grows.
    2. FLAT_PEEL       -- Encoding A, iterative greedy SIC / matching pursuit: global argmax, DEFLATE
                          book[argmax] from the running residual, repeat J times. NO slots. Cancellation
                          WITHOUT theta-gamma structure -- isolates whether cancellation alone helps.
    3. SLOT_NODEFLATE  -- Encoding B, per-slot unbind + argmax, NO cancellation (slotting alone).
    4. SLOT_PEEL_FIXED -- Encoding B, per-slot peel in FIXED slot order 0..J-1 (the resonator cell's
                          exact slot_decode_peel loop, retargeted to shared vocab). Tests whether naive
                          (unordered) cancellation transfers to high-J bundling.
    5. SLOT_PEEL_POWER -- Encoding B, per-slot peel in DESCENDING per-slot CONFIDENCE order (SPARC/SIC
                          "decoding wave": resolve the most-confident slot first, defer uncertain ones).

  Metric per arm = SET RECALL = |predicted_set intersect true_set| / J  (items sampled w/o replacement).

MECHANISM DISSOCIATION the FULL run delivers (this is WHY there are 5 arms, not 3):
    FLAT_PEEL   >> FLAT_TOPJ         => cancellation (matching pursuit) helps additive bundling.
    SLOT_NODEFLATE <= FLAT_TOPJ      => slotting ALONE does not help (drill's dissociation).
    SLOT_PEEL_POWER ~ FLAT_PEEL      => theta-gamma SLOTS add nothing on top of cancellation.
    SLOT_PEEL_FIXED < SLOT_PEEL_POWER => ORDERING is the load-bearing part of cancellation.

PILOT CALIBRATION (clean near-orthogonal FHRR phasor codes; scratchpad, this session; drives the bands):
  - Clean random codes DO NOT reproduce the real encoder's ~0.20@J8 collapse: FLAT_TOPJ holds ~1.0 out
    to J >> capacity; the real 0.20 is an encoder-EMBEDDING-GEOMETRY (correlation-law) artifact, NOT a
    clean-code capacity limit. Reproduced here honestly: FLAT_TOPJ degrades gracefully with J (never
    cliffs to 0.20 in clean synthetic). The discriminator is the ARM GAP at the shoulder, not a 0.20 floor.
  - N=192 V=600 J=32: FLAT_TOPJ~0.86  FLAT_PEEL~1.00  SLOT_PEEL_POWER~0.99  SLOT_PEEL_FIXED~0.71
    SLOT_NODEFLATE~0.64  (cancellation lift +0.14; ordering lift +0.28 over fixed; slots add nothing).
  - Naive fixed-order peel CATASTROPHICALLY mis-deflates past the reliable-decode threshold (early wrong
    pick deflates the wrong codeword -> injects noise); confidence-ordering repairs it.
  PILOT numbers above are MEASURED@scratchpad calibration (not this cell's metrics.json); the cell's own
  FULL run re-measures on disk. Bands below are HYPOTHESIZED from the pilot.

CONTRACT MAPPING (drill pre-reg -> this cell):
  CAPABILITY HARD-PASS (bundling wall beaten): at the shoulder-J (0.70 <= FLAT_TOPJ_mean <= 0.90) the best
    cancellation arm max(FLAT_PEEL, SLOT_PEEL_POWER) >= FLAT_TOPJ + 0.10 AND >= 0.95, cv <= 0.10.
  MECHANISM ATTRIBUTION (reported; refines the drill's theta-gamma claim):
    slotting_alone_null : SLOT_NODEFLATE <= FLAT_TOPJ + 0.05
    slots_unnecessary   : |SLOT_PEEL_POWER - FLAT_PEEL| <= 0.05  (attribute to CANCELLATION not slotting)
    ordering_loadbearing: SLOT_PEEL_POWER - SLOT_PEEL_FIXED >= 0.10
  HARD-FAIL (wall stands): best cancellation arm <= FLAT_TOPJ + 0.05 at every (N,J) -> cancellation does
    not transfer to additive bundling; two-head fixed-N wall confirmed fundamental.

CORRELATION-HURTS-ASSOCIATIVE-STORE-CAPACITY LAW compliance (reference_correlation_hurts...): the SLOT
  carriers are random near-orthogonal phasors -- they do NOT inject semantic correlation into the store
  side. The item codebook is near-orthogonal random (clean synthetic per USER "smoke clean synthetic"
  rule). No store-side correlation is re-injected by the mechanism. Asserted in _selftest.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (5 arms produce distinct winner sets)
# - final_metrics_atomicity: tmp_replace (write_metrics) + per-seed partials
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - discriminator_reachability: bands bracket the shoulder lift; HP threshold reachable (pilot-grounded)
# - baseline_in_band: FLAT_TOPJ must land 0.70..0.90 at >=1 (N,J) shoulder (discriminator fires)
# - discriminator survives scale: smoke at reduced N/J/seeds but SAME arms + same code path
# - cardinality_ok: EXPECTED_N_UNITS = sum over (seed, N, J)
# - PAIRED trials: identical vocab codebook + true item set across all 5 arms per trial
# - progress_logging: print_flush_true + heartbeat
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ (see docstring)
ASCII-only. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, json, argparse, time, traceback, platform, hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "bundling_slot_peel_sic_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- config -----------------------------------------------------------------
# J-grid per N straddles that N's capacity shoulder (FLAT_TOPJ 0.9 -> 0.7). Larger N -> larger shoulder.
if SMOKE:
    V = 1000
    J_BY_N = {192: [16, 32, 48]}
    TR = 20
    SEEDS = [7, 13]
else:
    V = 2000
    J_BY_N = {256: [8, 16, 32, 48, 64], 512: [16, 32, 64, 96]}
    TR = 60
    SEEDS = [7, 13, 19]

N_GRID = sorted(J_BY_N.keys())

# cardinality gate (META_RULE_H): one unit per (seed, N, J)
EXPECTED_N_UNITS = sum(len(J_BY_N[n]) for n in N_GRID) * len(SEEDS)

ARMS = ["FLAT_TOPJ", "FLAT_PEEL", "SLOT_NODEFLATE", "SLOT_PEEL_FIXED", "SLOT_PEEL_POWER"]

# band thresholds (HYPOTHESIZED@this prereg from pilot calibration)
SHOULDER_LO, SHOULDER_HI = 0.70, 0.90     # FLAT_TOPJ in-band window that defines the shoulder-J
CANCEL_LIFT_HP = 0.10                       # best cancellation arm >= FLAT_TOPJ + this at shoulder
CANCEL_ABS_HP = 0.95                        # ...and absolute >= this
NODEFLATE_NULL_MARGIN = 0.05                # SLOT_NODEFLATE <= FLAT_TOPJ + this (slotting-alone null)
SLOTS_EQUIV_TOL = 0.05                      # |SLOT_PEEL_POWER - FLAT_PEEL| <= this (slots unnecessary)
ORDERING_LB = 0.10                          # SLOT_PEEL_POWER - SLOT_PEEL_FIXED >= this (ordering matters)
CV_MAX = 0.10


# --- FHRR phasor primitives (VERBATIM style from theta_gamma v2 / resonator peel cells) -------
def phasor(m: int, d: int, rng: np.random.Generator) -> np.ndarray:
    """Random unit-modulus complex codebook (m, d) complex128."""
    ang = (rng.random((m, d)) * 2 - 1) * np.pi
    return np.exp(1j * ang)


def _cleanup_scores(probe: np.ndarray, bconj: np.ndarray) -> np.ndarray:
    """Real cleanup score of probe (N,) vs precomputed conj(book) bconj (V,N) -> (V,). N at match."""
    return (bconj @ probe).real


# --- arm decoders (all return a set of predicted vocab indices) --------------
# NOTE: `book` is the (V,N) codebook; `bconj` = np.conj(book) precomputed once per unit (V,N);
#       `sconj` = np.conj(slots) precomputed once per unit (J,N). Semantics identical to the naive
#       per-call np.conj forms; only precomputed for speed (verified bit-equal by _selftest).
def decode_flat_topj(Sf: np.ndarray, book: np.ndarray, bconj: np.ndarray,
                     slots: np.ndarray, sconj: np.ndarray, J: int) -> set:
    sc = _cleanup_scores(Sf, bconj)
    return set(int(x) for x in np.argpartition(-sc, J)[:J])


def decode_flat_peel(Sf: np.ndarray, book: np.ndarray, bconj: np.ndarray,
                     slots: np.ndarray, sconj: np.ndarray, J: int) -> set:
    """Iterative greedy SIC / matching pursuit. NO slots. Global argmax -> deflate -> repeat J times."""
    residual = Sf.copy()
    preds: List[int] = []
    for _ in range(J):
        sc = _cleanup_scores(residual, bconj)
        for u in preds:
            sc[u] = -1e18                       # never repick a resolved codeword
        ih = int(np.argmax(sc))
        preds.append(ih)
        residual = residual - book[ih]          # DEFLATE resolved item (unit-weight matching pursuit)
    return set(preds)


def decode_slot_nodeflate(Ss: np.ndarray, book: np.ndarray, bconj: np.ndarray,
                          slots: np.ndarray, sconj: np.ndarray, J: int) -> set:
    """Per-slot unbind + argmax, NO cancellation (slotting alone). Batched over slots (one matmul)."""
    probes = Ss[None, :] * sconj                 # (J,N)
    scores = (probes @ bconj.T).real             # (J,V)
    return set(int(x) for x in np.argmax(scores, axis=1))


def decode_slot_peel_fixed(Ss: np.ndarray, book: np.ndarray, bconj: np.ndarray,
                           slots: np.ndarray, sconj: np.ndarray, J: int) -> set:
    """Per-slot peel in FIXED slot order 0..J-1 (retarget of resonator slot_decode_peel to shared vocab)."""
    residual = Ss.copy()
    preds: List[int] = []
    for j in range(J):
        probe = residual * sconj[j]
        ih = int(np.argmax(_cleanup_scores(probe, bconj)))
        preds.append(ih)
        residual = residual - slots[j] * book[ih]     # DEFLATE resolved item from its slot
    return set(preds)


def decode_slot_peel_power(Ss: np.ndarray, book: np.ndarray, bconj: np.ndarray,
                           slots: np.ndarray, sconj: np.ndarray, J: int) -> set:
    """Per-slot peel in DESCENDING confidence order (SPARC/SIC decoding wave): each round resolve the
    slot whose current best cleanup score is highest; deflate; continue. Batched cleanup per round."""
    residual = Ss.copy()
    remaining = list(range(J))
    preds: List[int] = []
    while remaining:
        rem = np.array(remaining)
        probes = residual[None, :] * sconj[rem]          # (R,N)
        scores = (probes @ bconj.T).real                 # (R,V)
        best_m = np.argmax(scores, axis=1)               # (R,) best codeword per remaining slot
        best_vals = scores[np.arange(len(rem)), best_m]  # (R,)
        w = int(np.argmax(best_vals))                    # which remaining slot is most confident
        best_j = int(rem[w]); best_ih = int(best_m[w])
        preds.append(best_ih)
        residual = residual - slots[best_j] * book[best_ih]
        remaining.remove(best_j)
    return set(preds)


ARM_DECODERS = {
    "FLAT_TOPJ": decode_flat_topj,
    "FLAT_PEEL": decode_flat_peel,
    "SLOT_NODEFLATE": decode_slot_nodeflate,
    "SLOT_PEEL_FIXED": decode_slot_peel_fixed,
    "SLOT_PEEL_POWER": decode_slot_peel_power,
}


def _hash_sets(list_of_sets: List[set]) -> str:
    flat = ";".join(",".join(str(x) for x in sorted(s)) for s in list_of_sets)
    return hashlib.sha256(flat.encode("utf-8")).hexdigest()


# --- self-test ---------------------------------------------------------------
def _selftest() -> None:
    import numpy as _n
    rng = _n.random.default_rng(0)
    N, Vt, J = 128, 300, 6
    book = phasor(Vt, N, rng)
    slots = phasor(J, N, _n.random.default_rng(999))
    # 1. phasor unit modulus
    assert _n.allclose(_n.abs(book), 1.0), "phasor unit modulus"
    # 2. slot carriers near-orthogonal (correlation-law: no store correlation injected by slots)
    g = _n.abs(_n.conj(slots[0]) @ slots[1]) / N
    assert g < 0.30, "slot carriers must be near-orthogonal (no correlation injection), got %.3f" % g
    # 3. easy regime (J small, ample N): every arm recovers the full set exactly
    items = _n.array([5, 40, 120, 200, 260, 11], dtype=_n.int64)
    ts = set(int(x) for x in items)
    Sf = book[items].sum(0)
    Ss = (slots * book[items]).sum(0)
    bconj = _n.conj(book); sconj = _n.conj(slots)
    for arm in ARMS:
        enc = Sf if arm.startswith("FLAT") else Ss
        got = ARM_DECODERS[arm](enc, book, bconj, slots, sconj, J)
        assert got == ts, "arm %s must recover full set at easy regime; got %s" % (arm, sorted(got))
    # 4. FLAT_PEEL deflation invariant: after removing the resolved codeword, that codeword's score drops
    residual = Sf.copy()
    sc0 = _cleanup_scores(residual, bconj)
    ih0 = int(_n.argmax(sc0))
    assert ih0 in ts, "matching-pursuit first pick must be a true member at easy regime"
    residual = residual - book[ih0]
    assert _cleanup_scores(residual, bconj)[ih0] < 0.5 * N, "deflation must suppress the resolved codeword score"
    # 5. SLOT peel deflation invariant: removing slot-bound resolved item preserves remaining slot bindings
    residual = Ss.copy()
    probe0 = residual * _n.conj(slots[0])
    ih = int(_n.argmax(_cleanup_scores(probe0, bconj)))
    assert ih == int(items[0]), "slot-0 unbind must resolve item 0 at easy regime"
    residual = residual - slots[0] * book[ih]
    remaining = _n.zeros(N, dtype=_n.complex128)
    for k in range(1, J):
        remaining += slots[k] * book[int(items[k])]
    assert _n.allclose(residual, remaining, atol=1e-9), "SLOT deflation invariant violated"
    # 6. set-recall metric sanity
    assert len({1, 2, 3} & {2, 3, 9}) / 3 == 2 / 3, "set-recall metric"
    # 7. TELEMETRY-SENSITIVITY: perturbing the encoding must move at least one arm's output (not pinned)
    Sf_pert = Sf + 0.8 * book[7]      # inject a non-member with weight -> FLAT_TOPJ should shift
    base = decode_flat_topj(Sf, book, bconj, slots, sconj, J)
    pert = decode_flat_topj(Sf_pert, book, bconj, slots, sconj, J)
    assert base != pert, "telemetry-sensitivity: FLAT_TOPJ must respond to an injected non-member"
    print("[selftest] PASS: bundling-slot-peel-sic (7 groups; arms recover easy regime, deflation "
          "invariants hold, slots near-orthogonal, telemetry-sensitive)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# --- defensive instrumentation ----------------------------------------------
def _write_start_marker(output_dir: Path, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units, "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"; final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra: Dict) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": time.perf_counter() - t0}
    row.update(extra)
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"; final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def run_unit(N: int, J: int, seed: int) -> Tuple[Dict[str, float], Dict[str, str]]:
    """One (N,J) unit for one seed. PAIRED: same vocab codebook + true item sets across all 5 arms."""
    rng = np.random.default_rng(seed * 100003 + N * 17 + J)
    book = phasor(V, N, rng)
    slots = phasor(J, N, np.random.default_rng(seed * 7777 + N * 31 + J))
    bconj = np.conj(book)                                 # (V,N) precomputed once per unit
    sconj = np.conj(slots)                                # (J,N) precomputed once per unit
    recall = {a: 0.0 for a in ARMS}
    winner_sets = {a: [] for a in ARMS}
    for _t in range(TR):
        items = rng.choice(V, size=J, replace=False)
        true_set = set(int(x) for x in items)
        Sf = book[items].sum(0)
        Ss = (slots * book[items]).sum(0)
        for arm in ARMS:
            enc = Sf if arm.startswith("FLAT") else Ss
            pred = ARM_DECODERS[arm](enc, book, bconj, slots, sconj, J)
            recall[arm] += len(pred & true_set) / J
            if _t < 8:                                   # keep a bounded winner sample for arm-hash
                winner_sets[arm].append(pred)
    recall = {a: recall[a] / TR for a in ARMS}
    hashes = {a: _hash_sets(winner_sets[a]) for a in ARMS}
    return recall, hashes


def run_seed(seed: int, output_dir: Path, t0_start: float, unit_base: int, total_units: int) -> Dict:
    by_cell: Dict[str, Dict] = {}
    arms_hashes: Dict[str, str] = {}
    unit = unit_base
    for N in N_GRID:
        for J in J_BY_N[N]:
            recall, hashes = run_unit(N, J, seed)
            key = "N%d_J%d" % (N, J)
            by_cell[key] = {"N": N, "J": J, "TR": TR, "recall": recall}
            for a in ARMS:
                arms_hashes["%s_%s" % (key, a)] = hashes[a]
            unit += 1
            _heartbeat(output_dir, unit, total_units, t0_start,
                       {"seed": seed, "N": N, "J": J,
                        "FLAT_TOPJ": recall["FLAT_TOPJ"], "FLAT_PEEL": recall["FLAT_PEEL"],
                        "SLOT_PEEL_POWER": recall["SLOT_PEEL_POWER"]})
            print("  seed=%d N=%d J=%2d | FLAT_TOPJ=%.3f FLAT_PEEL=%.3f SLOT_ND=%.3f "
                  "SLOT_FIX=%.3f SLOT_POW=%.3f" %
                  (seed, N, J, recall["FLAT_TOPJ"], recall["FLAT_PEEL"], recall["SLOT_NODEFLATE"],
                   recall["SLOT_PEEL_FIXED"], recall["SLOT_PEEL_POWER"]), flush=True)
    return {"seed": seed, "by_cell": by_cell, "arms_hashes": arms_hashes,
            "V": V, "run_mode": RUN_MODE}


# --- verdict -----------------------------------------------------------------
def _mean_over_seeds(per_seed: List[Dict], key: str, arm: str) -> float:
    return float(np.mean([ps["by_cell"][key]["recall"][arm] for ps in per_seed]))


def _cv_over_seeds(per_seed: List[Dict], key: str, arm: str) -> float:
    vals = np.array([ps["by_cell"][key]["recall"][arm] for ps in per_seed])
    m = float(vals.mean())
    if abs(m) < 1e-9:
        return 0.0
    return float(vals.std() / (abs(m) + 1e-12))


def build_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    keys = list(per_seed[0]["by_cell"].keys())
    traj: Dict[str, Dict] = {}
    for key in keys:
        traj[key] = {a: _mean_over_seeds(per_seed, key, a) for a in ARMS}
        traj[key]["N"] = per_seed[0]["by_cell"][key]["N"]
        traj[key]["J"] = per_seed[0]["by_cell"][key]["J"]

    # shoulder-J per N = smallest J whose FLAT_TOPJ_mean is in [SHOULDER_LO, SHOULDER_HI]
    shoulders: Dict[int, str] = {}
    for N in N_GRID:
        cand = [k for k in keys if traj[k]["N"] == N]
        cand.sort(key=lambda k: traj[k]["J"])
        chosen = None
        for k in cand:
            if SHOULDER_LO <= traj[k]["FLAT_TOPJ"] <= SHOULDER_HI:
                chosen = k
                break
        if chosen is None:                                    # else use the lowest FLAT_TOPJ cell
            chosen = min(cand, key=lambda k: traj[k]["FLAT_TOPJ"])
        shoulders[N] = chosen

    detail = {"trajectory": traj, "shoulders": shoulders,
              "bands": {"shoulder_window": [SHOULDER_LO, SHOULDER_HI], "cancel_lift_hp": CANCEL_LIFT_HP,
                        "cancel_abs_hp": CANCEL_ABS_HP, "nodeflate_null_margin": NODEFLATE_NULL_MARGIN,
                        "slots_equiv_tol": SLOTS_EQUIV_TOL, "ordering_lb": ORDERING_LB, "cv_max": CV_MAX}}

    # discriminator-fires gate (META_RULE_AG / contract): FLAT_TOPJ must actually degrade somewhere
    min_flat = min(traj[k]["FLAT_TOPJ"] for k in keys)
    discriminator_fires = min_flat <= SHOULDER_HI
    detail["min_flat_topj"] = min_flat
    detail["discriminator_fires"] = bool(discriminator_fires)

    # per-shoulder capability + attribution
    per_shoulder = {}
    cap_pass_any = False
    for N in N_GRID:
        k = shoulders[N]
        t = traj[k]
        best_cancel = max(t["FLAT_PEEL"], t["SLOT_PEEL_POWER"])
        best_cancel_arm = "FLAT_PEEL" if t["FLAT_PEEL"] >= t["SLOT_PEEL_POWER"] else "SLOT_PEEL_POWER"
        cv_best = _cv_over_seeds(per_seed, k, best_cancel_arm)
        cap = (best_cancel >= t["FLAT_TOPJ"] + CANCEL_LIFT_HP and best_cancel >= CANCEL_ABS_HP
               and cv_best <= CV_MAX)
        cap_pass_any = cap_pass_any or cap
        per_shoulder[str(N)] = {
            "shoulder_cell": k, "J": t["J"], "FLAT_TOPJ": t["FLAT_TOPJ"],
            "FLAT_PEEL": t["FLAT_PEEL"], "SLOT_NODEFLATE": t["SLOT_NODEFLATE"],
            "SLOT_PEEL_FIXED": t["SLOT_PEEL_FIXED"], "SLOT_PEEL_POWER": t["SLOT_PEEL_POWER"],
            "best_cancel": best_cancel, "best_cancel_arm": best_cancel_arm,
            "cancel_lift_vs_flat": best_cancel - t["FLAT_TOPJ"], "cv_best": cv_best,
            "capability_pass": bool(cap),
            "slotting_alone_null": bool(t["SLOT_NODEFLATE"] <= t["FLAT_TOPJ"] + NODEFLATE_NULL_MARGIN),
            "slots_unnecessary": bool(abs(t["SLOT_PEEL_POWER"] - t["FLAT_PEEL"]) <= SLOTS_EQUIV_TOL),
            "ordering_loadbearing": bool(t["SLOT_PEEL_POWER"] - t["SLOT_PEEL_FIXED"] >= ORDERING_LB),
        }
    detail["per_shoulder"] = per_shoulder

    # HARD-FAIL: best cancellation arm never clears FLAT+0.05 at ANY (N,J)
    ever_beats = any(max(traj[k]["FLAT_PEEL"], traj[k]["SLOT_PEEL_POWER"]) > traj[k]["FLAT_TOPJ"] + 0.05
                     for k in keys)
    detail["cancellation_ever_beats_flat"] = bool(ever_beats)

    traj_str = " ".join(
        "%s(FT=%.2f,FP=%.2f,ND=%.2f,SF=%.2f,SP=%.2f)" %
        (k, traj[k]["FLAT_TOPJ"], traj[k]["FLAT_PEEL"], traj[k]["SLOT_NODEFLATE"],
         traj[k]["SLOT_PEEL_FIXED"], traj[k]["SLOT_PEEL_POWER"]) for k in keys)

    if not discriminator_fires:
        return ("MIDDLE_BAND",
                "VACUOUS_DISCRIMINATOR (META_RULE_AG): FLAT_TOPJ never dropped into/below the shoulder "
                "window (min=%.3f > %.2f) -- regime too easy; arm gap not exercised. Raise J / lower N. "
                "traj: %s" % (min_flat, SHOULDER_HI, traj_str), detail)

    if not ever_beats:
        return ("HARD_FAIL",
                "HARD_FAIL_WALL_STANDS: cancellation never beats FLAT_TOPJ by >0.05 at any (N,J). "
                "Successive cancellation does NOT transfer to additive bundling at this regime; the "
                "two-head fixed-N wall is confirmed fundamental. traj: %s" % traj_str, detail)

    if cap_pass_any:
        # summarise mechanism attribution across shoulders
        attr = per_shoulder[str(N_GRID[-1])]
        return ("HARD_PASS",
                "BUNDLING_WALL_BEATEN (HARD_PASS): confidence-ordered successive cancellation raises "
                "J-item bundling recall above flat top-J readout at the capacity shoulder "
                "(best_cancel=%.3f vs FLAT_TOPJ=%.3f, lift=%.3f, cv=%.3f). MECHANISM: slotting_alone_null=%s "
                "(SLOT_NODEFLATE<=FLAT+.05), slots_unnecessary=%s (SLOT_PEEL_POWER~FLAT_PEEL -> attribute to "
                "CANCELLATION not theta-gamma slots), ordering_loadbearing=%s (POWER>>FIXED). traj: %s" %
                (attr["best_cancel"], attr["FLAT_TOPJ"], attr["cancel_lift_vs_flat"], attr["cv_best"],
                 attr["slotting_alone_null"], attr["slots_unnecessary"], attr["ordering_loadbearing"],
                 traj_str), detail)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: cancellation beats flat at some (N,J) but does not clear the full capability "
            "bar (lift>=%.2f AND abs>=%.2f AND cv<=%.2f) at any shoulder. Real but modest bundling-capacity "
            "lift; ordering/regime tuning may sharpen it. traj: %s" %
            (CANCEL_LIFT_HP, CANCEL_ABS_HP, CV_MAX, traj_str), detail)


def main() -> None:
    output_dir = get_output_dir(ANCHOR_NAME)
    total_units = EXPECTED_N_UNITS
    _write_start_marker(output_dir, total_units)
    print("[config] anchor=%s mode=%s V=%d N_GRID=%s J_BY_N=%s TR=%d seeds=%s expected_units=%d" %
          (ANCHOR_NAME, RUN_MODE, V, N_GRID, J_BY_N, TR, SEEDS, total_units), flush=True)

    t0_start = time.perf_counter()
    run_config = {"V": V, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, output_dir, run_config=run_config)
    print("[ckpt] %d/%d seeds done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    units_per_seed = sum(len(J_BY_N[n]) for n in N_GRID)
    for i, seed in enumerate(remaining):
        res = run_seed(seed, output_dir, t0_start,
                       unit_base=(len(done) + i) * units_per_seed, total_units=total_units)
        res["config_version"] = "ANCHOR=%s,V=%d,N=%s" % (ANCHOR_NAME, V, N_GRID)
        res["run_mode"] = RUN_MODE
        write_partial(output_dir, seed, res)

    per_seed = list(aggregate_partials(output_dir, SEEDS, run_config=run_config).values())
    if len(per_seed) != len(SEEDS):
        raise RuntimeError("HARD_FAIL_CARDINALITY_META_RULE_H: expected %d seeds, got %d"
                           % (len(SEEDS), len(per_seed)))
    for ps in per_seed:
        if len(ps["by_cell"]) != units_per_seed:
            raise RuntimeError("HARD_FAIL_CARDINALITY_META_RULE_H: seed %s has %d cells, expected %d"
                               % (ps.get("seed"), len(ps["by_cell"]), units_per_seed))

    # ARMS-MUST-DIFFER (META_RULE_AF): the 5 arms must not be bit-identical at the hardest cell
    ref = per_seed[0]["arms_hashes"]
    hardest = min(per_seed[0]["by_cell"].keys(),
                  key=lambda k: per_seed[0]["by_cell"][k]["recall"]["FLAT_TOPJ"])
    hlist = [ref["%s_%s" % (hardest, a)] for a in ARMS]
    n_distinct = len(set(hlist))
    arms_differ_ok = n_distinct >= 3          # >=3 of 5 arm-winner-sets distinct at the hardest cell
    if not arms_differ_ok:
        raise RuntimeError("META_RULE_AF VIOLATION: only %d distinct arm-winner-sets at hardest cell %s "
                           "(arms collapsed to near-identical outputs; implementation bug)"
                           % (n_distinct, hardest))

    verdict, vmsg, detail = build_verdict(per_seed)
    detail["arms_differ_verified"] = bool(arms_differ_ok)
    detail["arms_distinct_at_hardest"] = int(n_distinct)
    detail["hardest_cell"] = hardest

    if SMOKE and not detail.get("discriminator_fires", False):
        print("[SMOKE_GATE_FAIL] discriminator did NOT fire: FLAT_TOPJ never entered shoulder window "
              "(min=%.3f). DO NOT dispatch FULL; raise J / lower N." % detail["min_flat_topj"], flush=True)

    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
        "summary": verdict, "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "per_seed": per_seed, "detail": detail,
        "config": {"V": V, "N_GRID": N_GRID, "J_BY_N": {str(k): v for k, v in J_BY_N.items()},
                   "TR": TR, "SEEDS": SEEDS, "ARMS": ARMS, "EXPECTED_N_UNITS": EXPECTED_N_UNITS},
        "elapsed_s": time.perf_counter() - t0_start,
    }
    write_metrics(output_dir, metrics, per_seed)
    print("[metrics] written -> %s" % (output_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, e)
        raise
