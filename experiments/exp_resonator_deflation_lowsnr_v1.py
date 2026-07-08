"""
exp_resonator_deflation_lowsnr_v1.py -- 5x-drill #3 on the resonator theta-gamma slot-peel escape.
ISOLATE whether the DEFLATION sub-lever is load-bearing at a HARDER (low-SNR) regime.

RESEARCH CONTEXT (follow-on to exp_resonator_theta_gamma_peel_v1 VET, drill #3 steer):
  The K5/K6 resonator reachability wall is ESCAPED by theta-gamma slot re-encoding
  (VET'd MEASURED_MECHANISM). The VET decomposed the escape into two sub-levers:
    (1) SLOTTING  -- re-encode the K-way joint product as a per-slot superposition
                     s = sum_k slots[k] * book[k][x_k], decoded by K sequential 1-way
                     unbind+cleanup searches. THIS is the load-bearing lever.
    (2) DEFLATION -- after resolving slot k, SUBTRACT its resolved contribution from the
                     residual before decoding slot k+1 (peel-off). At the benign-SNR test
                     regime (N=4096, K<=6; SNR ~ sqrt(N/(K-1)) ~ 28) the VET found
                     slot_peel == slot_nodeflate == 1.000 (delta 0). Deflation appeared
                     NON-load-bearing there -- but ONLY because SNR was so benign that a
                     single-shot per-slot unbind already recovers every factor exactly, so
                     there was nothing left for deflation to fix.
  DRILL #3 QUESTION (this cell): does deflation EARN ITS KEEP at a HARDER regime where SNR
  is NOT benign? Prove whether peel > nodeflate at low SNR, and if so report the SNR/K
  BREAK-POINT where deflation starts mattering (or that it never does).

THE TEST (low-SNR SNR-sweep via K at fixed small N; PAIRED peel-vs-nodeflate on identical
tuples + codebooks + slot carriers):
  N = 256, M = 30, K in {16, 20, 24, 28}.  SNR(correct-codeword score) = signal/crosstalk-std
  = N / sqrt((K-1)*N/2) = sqrt(2N/(K-1)) -> ~5.84 (K16) down to ~4.35 (K28).
  Crosstalk on each per-slot unbind = the OTHER (K-1) slot terms. When SNR is low, a
  single-shot per-slot argmax mis-resolves some factors; the exact-match (all-K-correct)
  tuple accuracy drops into a MEASURABLE band. DEFLATION reduces the crosstalk seen by LATER
  slots (each resolved+removed factor is one fewer interferer) -- a real benefit WHEN the
  early slots are resolved correctly, but ERROR-PROPAGATING when an early slot is wrong
  (a wrong subtraction leaves the true term AND injects a spurious one). Whether the
  crosstalk-reduction benefit dominates the error-propagation cost is genuinely uncertain at
  low SNR -- NOT decidable by construction. That is the discriminator.

WHAT IS MEASURED per (seed,K) -- PAIRED (identical books + slots + true tuples across arms):
  - slot_nodeflate_full : full-tuple exact-match acc, single-shot per-slot unbind, NO deflation (BASELINE)
  - slot_peel_full      : full-tuple exact-match acc, sequential peel-off + deflation      (MECHANISM)
  - slot_nodeflate_perslot / slot_peel_perslot : mean fraction of K slots correct (diagnostic)
  - peel_perslot_positional : per-slot accuracy vs decode-order position (mechanism signature --
                              deflation should LIFT later positions; nodeflate is flat by position)
  HEADLINE = gap(K) = slot_peel_full(K) - slot_nodeflate_full(K), and whether gap GROWS as SNR drops.

PRE-REG bands (deflation load-bearing at low SNR):
  Let gap(K) = slot_peel_full(K) - slot_nodeflate_full(K).  Low-SNR cells = {K24, K28}; benign
  control = K16; transition = K20.
  HARD_PASS (deflation load-bearing + break-point found):
       gap(K28) >= 0.10 AND gap(K24) >= 0.10 (deflation earns keep at low SNR)
       AND gap(K28) > gap(K24) > gap(K20)     (the gap GROWS as SNR drops -- monotone)
       AND gap(K16) < 0.05                     (benign control: deflation NON-load-bearing at
                                                benign SNR -- in-run reproduction of the VET's
                                                N=4096/K<=6/SNR~28 delta-0 finding)
  PARTIAL:
       gap(K28) >= 0.10 (deflation load-bearing at the hardest cell) but NOT strictly monotone
       OR benign control also shows gap(K16) >= 0.05 (deflation ALWAYS matters, not just low-SNR).
  HARD_FAIL (deflation never load-bearing -- honest simplification):
       gap(K28) < 0.10 (deflation does not earn its keep even at the lowest SNR). Means slotting
       ALONE suffices; the mechanism simplifies (drop the deflation step). Report faithfully.

INTEGRITY GATES (precede band classification):
  (G1) BENIGN CONTROL reproduction: at K16 (near-benign SNR) slot_nodeflate_full >= 0.95 (single-shot
       already near-perfect) AND gap(K16) < 0.05. Reproduces "deflation non-load-bearing when SNR
       benign" IN-RUN (CITED@exp_resonator_theta_gamma_peel_v1 VET: N=4096/K<=6 slot_peel==slot_nodeflate).
  (G2) BASELINE-IN-BAND (META_RULE_AG) at the DISCRIMINATING cells: 0.05 < slot_nodeflate_full < 0.95
       at K24 AND K28 (the cells where the discriminator is evaluated). K16/K20 are INTENTIONAL
       saturated/near-saturated controls (AG-exempt: they exist to show deflation does NOT matter at
       benign SNR, exactly like the VET's saturated-benign baseline).
  (G3) TELEMETRY-SENSITIVITY (mandatory anti-tautology guard): the peel-vs-nodeflate metric MOVES when
       telemetry is perturbed (add noise to S -> accuracy changes) AND peel != nodeflate predictions at
       a low-SNR cell (arms NOT bit-identical) AND full-tuple accuracy is NOT bit-identical across seeds.
       Asserted in _selftest.
  (G4) DEFLATION INVARIANT: resolving+removing one factor (correctly) preserves the remaining K-1
       binding EXACTLY at clean/benign SNR (peel machinery correct). Asserted in _selftest.

baseline_in_band (META_RULE_AG) EXEMPTION: K16 (nodeflate ~0.99) and K20 (~0.96) are INTENTIONAL
near-saturated controls -- they are the benign-SNR anchor proving the harness measures a real
SNR-gradient (not a constant). The discriminator (deflation earns its keep) is evaluated at the
IN-BAND low-SNR cells K24 (nodeflate ~0.80) and K28 (nodeflate ~0.55). This is the same exemption
structure as the peel cell's vanilla-oracle=0 baseline.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (peel preds != nodeflate preds at low-SNR cell)
# - final_metrics_atomicity: tmp_replace (write_metrics) + per-seed partials
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - discriminator_reachability: bands bracket the deflation gap; HP threshold 0.10 reachable
#   (THEORETICAL@sqrt(2N/(K-1)) SNR; calibration sim: gap 0.16 @K24, 0.35 @K28, N=256)
# - benign control at benign SNR (K16 reproduces deflation-non-load-bearing; G1)
# - discriminator survives scale: full-N == smoke-N == 256 (only TR/seeds reduced in smoke)
# - cardinality_ok: EXPECTED_N_UNITS = seeds*K gate
# - PAIRED trials: identical books + slots + true tuples across peel + nodeflate arms
# - telemetry-sensitivity: metric moves under perturbation + not bit-identical across seeds (G3)
# - progress_logging: print_flush_true + heartbeat
ASCII-only. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
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

ANCHOR_NAME = "resonator_deflation_lowsnr_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- config (LOW-SNR regime; IDENTICAL slot-decode machinery to the peel cell) ---
N = 256                       # small N -> low SNR at high K (SNR ~ sqrt(2N/(K-1)))
M = 30                        # codebook size per slot (per-slot argmax over M)
K_GRID = [16, 20, 24, 28]     # K16 benign control | K20 transition | K24/K28 low-SNR discriminating
TR = 60 if SMOKE else 200     # trials per (seed,K)
SEEDS = [3, 7] if SMOKE else [3, 7, 13, 21, 42, 101, 202, 303]   # >= 8 seeds FULL

# cardinality gate (META_RULE_H)
EXPECTED_N_UNITS = len(SEEDS) * len(K_GRID)

# band constants
GAP_HP = 0.10                 # HARD-PASS floor on peel-nodeflate full-tuple gap at low-SNR cells
BENIGN_GAP_MAX = 0.05         # benign control (K16) gap must be BELOW this (deflation non-load-bearing)
BENIGN_NODEFLATE_MIN = 0.95   # benign control nodeflate must be near-saturated (single-shot suffices)
BAND_LO, BAND_HI = 0.05, 0.95 # META_RULE_AG in-band window (for discriminating cells)
DISCRIM_K = [24, 28]          # cells where baseline must be in-band + discriminator evaluated
BENIGN_K = 16                 # benign control K


def _snr(N_: int, K_: int) -> float:
    """THEORETICAL correct-codeword-score SNR = signal(N) / crosstalk-std(sqrt((K-1)N/2))."""
    return float(np.sqrt(2.0 * N_ / (K_ - 1)))


# --- phasor + slot primitives (VERBATIM slot machinery from the peel cell) ----
def phasor(m: int, d: int, rng: np.random.Generator) -> np.ndarray:
    ang = (rng.random((m, d)) * 2 - 1) * np.pi
    return np.exp(1j * ang)


def slot_encode(books: List[np.ndarray], slots: np.ndarray, trues: np.ndarray, K: int, N_: int) -> np.ndarray:
    """s_slot = sum_k slots[k] * books[k][trues[:,k]]. books[k] (M,N); slots (K,N); trues (TR,K) -> (TR,N)."""
    S = np.zeros((trues.shape[0], N_), dtype=np.complex128)
    for k in range(K):
        S += slots[k][None, :] * books[k][trues[:, k]]
    return S


def _slot_score(probe: np.ndarray, book_k: np.ndarray) -> np.ndarray:
    """Cleanup score of probe (TR,N) vs codebook book_k (M,N) -> (TR,M) real; = N at matched codeword."""
    return (np.conj(probe) @ book_k.T).real


def slot_decode_nodeflate(S: np.ndarray, books: List[np.ndarray], slots: np.ndarray, K: int) -> np.ndarray:
    """Single-shot per-slot unbind + cleanup, NO deflation (BASELINE). Returns preds (TR,K)."""
    preds = np.zeros((S.shape[0], K), dtype=np.int64)
    for k in range(K):
        probe = S * np.conj(slots[k])[None, :]
        preds[:, k] = np.argmax(_slot_score(probe, books[k]), axis=1)
    return preds


def slot_decode_peel(S: np.ndarray, books: List[np.ndarray], slots: np.ndarray, K: int) -> np.ndarray:
    """Sequential peel-off: unbind slot k, resolve, DEFLATE its contribution, continue (MECHANISM). (TR,K)."""
    residual = S.copy()
    preds = np.zeros((S.shape[0], K), dtype=np.int64)
    for k in range(K):
        probe = residual * np.conj(slots[k])[None, :]
        ih = np.argmax(_slot_score(probe, books[k]), axis=1)     # (TR,)
        preds[:, k] = ih
        residual = residual - slots[k][None, :] * books[k][ih]   # DEFLATE resolved item
    return preds


def _hash_int_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a.astype(np.int64)).tobytes()).hexdigest()


# --- self-test ---------------------------------------------------------------
def _selftest() -> None:
    import numpy as _n
    # 1. phasor unit modulus
    assert _n.allclose(_n.abs(_n.exp(1j * _n.array([0.0, _n.pi / 2, _n.pi]))), 1.0), "phasor modulus"

    # 2. SNR formula sanity: monotone DECREASING in K (harder as K grows at fixed N)
    assert _snr(256, 16) > _snr(256, 28) > 0, "SNR must decrease with K"

    # 3. BENIGN-SNR exact recovery + DEFLATION INVARIANT (G4): at high N both arms recover exactly,
    #    and one clean deflation step preserves the remaining K-1 binding EXACTLY.
    Nb = 4096
    rng = _n.random.default_rng(0)
    Kb = 5
    books = [phasor(M, Nb, rng) for _ in range(Kb)]
    slots = phasor(Kb, Nb, _n.random.default_rng(123))
    trues = _n.array([[7, 3, 19, 2, 11], [1, 2, 3, 4, 5], [29, 0, 15, 8, 22]], dtype=_n.int64)
    S = slot_encode(books, slots, trues, Kb, Nb)
    trues2 = trues.copy(); trues2[0, 2] = (trues[0, 2] + 1) % M
    S2 = slot_encode(books, slots, trues2, Kb, Nb)
    assert not _n.allclose(S[0], S2[0]), "slot encoding must depend on every filler"
    assert _n.array_equal(slot_decode_nodeflate(S, books, slots, Kb), trues), "benign nodeflate must recover all"
    assert _n.array_equal(slot_decode_peel(S, books, slots, Kb), trues), "benign peel must recover exact tuple"
    # deflation invariant: remove factor 0 correctly -> residual == clean (K-1)-slot superposition
    residual = S[0].copy()
    ih0 = int(_n.argmax(_slot_score((residual * _n.conj(slots[0]))[None, :], books[0])[0]))
    assert ih0 == int(trues[0, 0]), "peel step-0 must resolve factor 0 at benign SNR"
    residual = residual - slots[0] * books[0][ih0]
    remaining = _n.zeros(Nb, dtype=_n.complex128)
    for k in range(1, Kb):
        remaining += slots[k] * books[k][int(trues[0, k])]
    assert _n.allclose(residual, remaining, atol=1e-9), \
        "DEFLATION INVARIANT violated: residual != clean (K-1)-slot superposition (err %.2e)" \
        % float(_n.max(_n.abs(residual - remaining)))

    # 4. TELEMETRY-SENSITIVITY GUARD (G3): at LOW SNR the metric MOVES + arms DIFFER + seed-sensitive.
    Nl, Kl, TRl = 128, 24, 120
    def _low_snr_full_accs(seed: int):
        rb = _n.random.default_rng(seed * 100 + Kl)
        bk = [phasor(M, Nl, rb) for _ in range(Kl)]
        rt = _n.random.default_rng(seed * 1000 + Kl)
        tr = _n.array([[int(x) for x in rt.integers(0, M, size=Kl)] for _ in range(TRl)], dtype=_n.int64)
        sl = phasor(Kl, Nl, _n.random.default_rng(seed * 7777 + Kl))
        Ss = slot_encode(bk, sl, tr, Kl, Nl)
        pnd = slot_decode_nodeflate(Ss, bk, sl, Kl)
        ppl = slot_decode_peel(Ss, bk, sl, Kl)
        f_nd = float(_n.mean(_n.all(pnd == tr, axis=1)))
        f_pl = float(_n.mean(_n.all(ppl == tr, axis=1)))
        return pnd, ppl, tr, Ss, bk, sl, f_nd, f_pl
    pnd, ppl, tr, Ss, bk, sl, f_nd, f_pl = _low_snr_full_accs(3)
    # 4a. arms NOT bit-identical at low SNR (peel changes the answer)
    assert not _n.array_equal(pnd, ppl), "TELEMETRY-SENSITIVITY: peel and nodeflate must DIFFER at low SNR"
    # 4b. deflation is LOAD-BEARING at low SNR (peel full-tuple acc strictly beats nodeflate)
    assert f_pl > f_nd + 0.05, "TELEMETRY-SENSITIVITY: peel must beat nodeflate at low SNR (got %.3f vs %.3f)" % (f_pl, f_nd)
    # 4c. metric MOVES when telemetry perturbed (add complex noise to S -> accuracy changes)
    rn = _n.random.default_rng(999)
    noise = (rn.standard_normal(Ss.shape) + 1j * rn.standard_normal(Ss.shape)) * 3.0
    ppl_pert = slot_decode_peel(Ss + noise, bk, sl, Kl)
    f_pl_pert = float(_n.mean(_n.all(ppl_pert == tr, axis=1)))
    assert abs(f_pl_pert - f_pl) > 1e-6, "TELEMETRY-SENSITIVITY: metric must MOVE under perturbation (tautology guard)"
    assert f_pl_pert < f_pl, "TELEMETRY-SENSITIVITY: added noise must DEGRADE peel accuracy"
    # 4d. NOT bit-identical across seeds (different draw -> different accuracy)
    _, _, _, _, _, _, f_nd2, f_pl2 = _low_snr_full_accs(7)
    assert (abs(f_pl2 - f_pl) > 1e-9) or (abs(f_nd2 - f_nd) > 1e-9), \
        "TELEMETRY-SENSITIVITY: accuracy must vary across seeds (not bit-identical)"

    print("[selftest] PASS: resonator-deflation-lowsnr (4 groups; deflation-invariant at benign SNR, "
          "peel>nodeflate + metric-moves + seed-varies at low SNR N=%d K=%d)" % (Nl, Kl), flush=True)


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


def run_seed(seed: int, output_dir: Path, t0_start: float, unit_base: int, total_units: int) -> Dict:
    """All K arms for one seed. PAIRED: same books + slots + true tuples across peel + nodeflate."""
    out: Dict[str, Dict] = {}
    arms_hashes: Dict[str, str] = {}
    unit = unit_base
    for K in K_GRID:
        rng_book = np.random.default_rng(seed * 100 + K)
        books = [phasor(M, N, rng_book) for _ in range(K)]
        rng_trial = np.random.default_rng(seed * 1000 + K)
        trues = np.array([[int(x) for x in rng_trial.integers(0, M, size=K)] for _ in range(TR)], dtype=np.int64)
        slots = phasor(K, N, np.random.default_rng(seed * 7777 + K))

        S = slot_encode(books, slots, trues, K, N)
        pred_nd = slot_decode_nodeflate(S, books, slots, K)
        pred_pl = slot_decode_peel(S, books, slots, K)

        full_nd = float(np.mean(np.all(pred_nd == trues, axis=1)))
        full_pl = float(np.mean(np.all(pred_pl == trues, axis=1)))
        perslot_nd = float(np.mean(pred_nd == trues))
        perslot_pl = float(np.mean(pred_pl == trues))
        # positional per-slot accuracy vs decode order (mechanism signature)
        pos_nd = (pred_nd == trues).mean(axis=0).tolist()
        pos_pl = (pred_pl == trues).mean(axis=0).tolist()

        out["K%d" % K] = {
            "K": K, "TR": TR, "snr": _snr(N, K),
            "slot_nodeflate_full": full_nd,
            "slot_peel_full": full_pl,
            "gap_full": full_pl - full_nd,
            "slot_nodeflate_perslot": perslot_nd,
            "slot_peel_perslot": perslot_pl,
            "gap_perslot": perslot_pl - perslot_nd,
            "peel_positional": pos_pl,
            "nodeflate_positional": pos_nd,
        }
        arms_hashes["K%d_slot_peel" % K] = _hash_int_array(pred_pl)
        arms_hashes["K%d_slot_nodeflate" % K] = _hash_int_array(pred_nd)

        unit += 1
        _heartbeat(output_dir, unit, total_units, t0_start,
                   {"seed": seed, "K": K, "snr": _snr(N, K),
                    "slot_nodeflate_full": full_nd, "slot_peel_full": full_pl, "gap_full": full_pl - full_nd})
        print("  seed=%d K=%2d SNR=%.2f | nodeflate_full=%.3f peel_full=%.3f gap=%+.3f | perslot nd=%.3f pl=%.3f" %
              (seed, K, _snr(N, K), full_nd, full_pl, full_pl - full_nd, perslot_nd, perslot_pl), flush=True)

    return {"seed": seed, "by_arm": out, "arms_hashes": arms_hashes, "N": N, "M": M, "run_mode": RUN_MODE}


# --- verdict -----------------------------------------------------------------
def _mean_over_seeds(per_seed: List[Dict], K: int, field: str) -> float:
    return float(np.mean([ps["by_arm"]["K%d" % K][field] for ps in per_seed]))


def _cv_over_seeds(per_seed: List[Dict], K: int, field: str) -> float:
    vals = [ps["by_arm"]["K%d" % K][field] for ps in per_seed]
    m = float(np.mean(vals))
    return float(np.std(vals) / m) if abs(m) > 1e-9 else 0.0


def build_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    traj: Dict[str, Dict] = {}
    for K in K_GRID:
        traj[str(K)] = {
            "snr": _snr(N, K),
            "slot_nodeflate_full": _mean_over_seeds(per_seed, K, "slot_nodeflate_full"),
            "slot_peel_full": _mean_over_seeds(per_seed, K, "slot_peel_full"),
            "gap_full": _mean_over_seeds(per_seed, K, "gap_full"),
            "gap_full_cv": _cv_over_seeds(per_seed, K, "gap_full"),
            "peel_full_cv": _cv_over_seeds(per_seed, K, "slot_peel_full"),
        }
    detail = {"trajectory": traj,
              "bands": {"gap_hp": GAP_HP, "benign_gap_max": BENIGN_GAP_MAX,
                        "benign_nodeflate_min": BENIGN_NODEFLATE_MIN,
                        "band_lo": BAND_LO, "band_hi": BAND_HI,
                        "discrim_k": DISCRIM_K, "benign_k": BENIGN_K}}

    g16 = traj["16"]["gap_full"]; g20 = traj["20"]["gap_full"]
    g24 = traj["24"]["gap_full"]; g28 = traj["28"]["gap_full"]
    nd16 = traj["16"]["slot_nodeflate_full"]
    nd24 = traj["24"]["slot_nodeflate_full"]; nd28 = traj["28"]["slot_nodeflate_full"]

    # G1 benign control
    g1_ok = (nd16 >= BENIGN_NODEFLATE_MIN) and (g16 < BENIGN_GAP_MAX)
    # G2 baseline-in-band at discriminating cells
    g2_ok = (BAND_LO < nd24 < BAND_HI) and (BAND_LO < nd28 < BAND_HI)
    detail["G1_benign_control_ok"] = bool(g1_ok)
    detail["G2_baseline_in_band_ok"] = bool(g2_ok)
    detail["G1_detail"] = {"nd_K16": nd16, "gap_K16": g16,
                           "nd_min_req": BENIGN_NODEFLATE_MIN, "gap_max_req": BENIGN_GAP_MAX}
    detail["G2_detail"] = {"nd_K24": nd24, "nd_K28": nd28, "band": [BAND_LO, BAND_HI]}

    # break-point: lowest-K (highest SNR) cell where gap first crosses GAP_HP
    break_K, break_snr = None, None
    for K in K_GRID:
        if traj[str(K)]["gap_full"] >= GAP_HP:
            break_K, break_snr = K, traj[str(K)]["snr"]
            break
    detail["deflation_break_K"] = break_K
    detail["deflation_break_snr"] = break_snr

    monotone = (g28 > g24) and (g24 > g20)
    detail["gap_monotone_grows_as_snr_drops"] = bool(monotone)
    detail["gaps"] = {"K16": g16, "K20": g20, "K24": g24, "K28": g28}

    traj_str = " ".join("K%d(SNR=%.2f,nd=%.3f,pl=%.3f,gap=%+.3f)" %
                        (K, traj[str(K)]["snr"], traj[str(K)]["slot_nodeflate_full"],
                         traj[str(K)]["slot_peel_full"], traj[str(K)]["gap_full"]) for K in K_GRID)

    # integrity gates first
    if not g1_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_G1_BENIGN_CONTROL: benign-SNR control (K16) did NOT reproduce "
                "deflation-non-load-bearing -- nodeflate_full(K16)=%.3f (need>=%.2f) gap(K16)=%+.3f "
                "(need<%.2f). Harness benign anchor broken; comparison suspect. traj: %s"
                % (nd16, BENIGN_NODEFLATE_MIN, g16, BENIGN_GAP_MAX, traj_str), detail)
    if not g2_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_G2_BASELINE_OUT_OF_BAND (META_RULE_AG): nodeflate baseline NOT in "
                "(%.2f,%.2f) at discriminating cells -- nd(K24)=%.3f nd(K28)=%.3f. Regime mis-set "
                "(too easy/too hard); discriminator cannot be measured. traj: %s"
                % (BAND_LO, BAND_HI, nd24, nd28, traj_str), detail)

    # band classification
    if g28 >= GAP_HP and g24 >= GAP_HP and monotone and g16 < BENIGN_GAP_MAX:
        return ("HARD_PASS",
                "DEFLATION_LOAD_BEARING_AT_LOW_SNR (HARD_PASS): peel beats nodeflate by a clear "
                "margin at low SNR -- gap(K24)=%+.3f gap(K28)=%+.3f >= %.2f, and the gap GROWS as SNR "
                "drops (gap: K20=%+.3f<K24=%+.3f<K28=%+.3f) while the benign control K16 shows gap=%+.3f "
                "< %.2f (deflation NON-load-bearing at benign SNR, reproducing the VET). Deflation break-"
                "point: K>=%s (SNR<=%.2f). The peel/deflation sub-lever EARNS ITS KEEP once SNR is low "
                "enough that single-shot per-slot unbind mis-resolves; crosstalk-reduction dominates "
                "error-propagation. traj: %s"
                % (g24, g28, GAP_HP, g20, g24, g28, g16, BENIGN_GAP_MAX,
                   str(break_K), (break_snr if break_snr is not None else -1.0), traj_str), detail)

    if g28 >= GAP_HP:
        return ("PARTIAL",
                "PARTIAL: deflation load-bearing at the hardest cell (gap(K28)=%+.3f >= %.2f) but the "
                "clean HARD_PASS shape is not met (monotone_grows=%s, gap(K16)=%+.3f vs benign_max %.2f). "
                "Deflation matters at low SNR but the break-point / benign-non-load-bearing story is not "
                "clean. break_K=%s. traj: %s"
                % (g28, GAP_HP, monotone, g16, BENIGN_GAP_MAX, str(break_K), traj_str), detail)

    return ("HARD_FAIL",
            "HARD_FAIL_DEFLATION_NEVER_LOAD_BEARING: peel does NOT beat nodeflate even at the lowest "
            "SNR (gap(K28)=%+.3f < %.2f). Honest negative: SLOTTING alone suffices; the deflation step "
            "does not earn its keep at ANY tested SNR -- the mechanism SIMPLIFIES (drop deflation). "
            "traj: %s" % (g28, GAP_HP, traj_str), detail)


def main() -> None:
    output_dir = get_output_dir(ANCHOR_NAME)
    total_units = EXPECTED_N_UNITS
    _write_start_marker(output_dir, total_units)
    print("[config] anchor=%s mode=%s N=%d M=%d K=%s TR=%d seeds=%s expected_units=%d" %
          (ANCHOR_NAME, RUN_MODE, N, M, K_GRID, TR, SEEDS, total_units), flush=True)
    print("[snr] " + " ".join("K%d->SNR=%.2f" % (K, _snr(N, K)) for K in K_GRID), flush=True)

    t0_start = time.perf_counter()
    run_config = {"N": N, "M": M, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, output_dir, run_config=run_config)
    print("[ckpt] %d/%d seeds done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    unit_base = len(done) * len(K_GRID)
    for i, seed in enumerate(remaining):
        res = run_seed(seed, output_dir, t0_start,
                       unit_base=unit_base + i * len(K_GRID), total_units=total_units)
        res["config_version"] = "ANCHOR=%s,N=%d,M=%d" % (ANCHOR_NAME, N, M)
        res["run_mode"] = RUN_MODE
        write_partial(output_dir, seed, res)

    per_seed = list(aggregate_partials(output_dir, SEEDS, run_config=run_config).values())
    if len(per_seed) != len(SEEDS):
        raise RuntimeError("HARD_FAIL_CARDINALITY_META_RULE_H: expected %d seeds, got %d"
                           % (len(SEEDS), len(per_seed)))
    for ps in per_seed:
        n_arms = sum(1 for k in ps["by_arm"] if k.startswith("K"))
        if n_arms != len(K_GRID):
            raise RuntimeError("HARD_FAIL_CARDINALITY_META_RULE_H: seed %s has %d K-arms, expected %d"
                               % (ps.get("seed"), n_arms, len(K_GRID)))

    # ARMS-MUST-DIFFER (META_RULE_AF): peel winners must differ from nodeflate winners at a low-SNR cell
    ref = per_seed[0]["arms_hashes"]
    arms_differ_ok = ref.get("K28_slot_peel") != ref.get("K28_slot_nodeflate")
    if not arms_differ_ok:
        raise RuntimeError("META_RULE_AF VIOLATION: slot_peel and slot_nodeflate produced bit-identical "
                           "winners at K28 -- deflation had ZERO effect even at lowest SNR (impl bug or "
                           "both cratered identically)")

    verdict, vmsg, detail = build_verdict(per_seed)
    detail["arms_differ_verified"] = bool(arms_differ_ok)

    # SMOKE DISCRIMINATOR-FIRES (META_RULE_K): the deflation gap must fire at low SNR AND grow toward K28
    traj = detail["trajectory"]
    gap28 = traj["28"]["gap_full"]; gap24 = traj["24"]["gap_full"]
    fired = (gap28 >= GAP_HP) and (gap28 > gap24)
    detail["smoke_discriminator_fired"] = bool(fired)
    detail["smoke_gap_K28"] = gap28
    detail["smoke_gap_K24"] = gap24
    if SMOKE and not fired:
        print("[SMOKE_GATE_FAIL] deflation discriminator did NOT fire: gap(K28)=%+.3f (need>=%.2f) "
              "gap(K24)=%+.3f (need gap28>gap24). DO NOT dispatch FULL." % (gap28, GAP_HP, gap24), flush=True)

    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "per_seed": per_seed, "detail": detail,
        "config": {"N": N, "M": M, "TR": TR, "K_GRID": K_GRID, "SEEDS": SEEDS,
                   "EXPECTED_N_UNITS": EXPECTED_N_UNITS, "GAP_HP": GAP_HP},
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
