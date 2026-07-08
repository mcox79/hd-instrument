"""
exp_resonator_theta_gamma_peel_v1.py -- 5x-drill #2 on the resonator K5/K6 wall.
THETA-GAMMA SEQUENTIAL RE-ENCODING (peel-off / deflation) vs the vanilla joint resonator.

RESEARCH CONTEXT (follow-on to exp_resonator_ksweep_reachability_v1 HARD_FAIL "WALL_FUNDAMENTAL"
+ notes/research_brain_grounding_resonator_basin_proliferation_2026-07-08.md candidate #2):
  The K5/K6 wall is skunkworks-confirmed a REACHABILITY / convergence-dynamics wall, NOT a
  crosstalk-capacity wall. Drill #1 (DG dimensional-expansion front-end,
  exp_resonator_dg_frontend_ksweep_v1) HARD_FAILed -- crosstalk / N-expansion / DG-frontend levers
  are PROVEN NON-LOAD-BEARING and larger restart-budget R is DEAD (K-sweep: 3600 restarts, 0 hits
  at K5, basin unreachable by vanilla joint dynamics regardless of R).
  MECHANISM: at K5/K6 the resonator's SIMULTANEOUS K-way joint factorization search cannot CONVERGE
  onto the correct attractor even though the answer is crosstalk-clean and findable-in-principle.
  Single-factor (K1) and low-K search WORK; the joint high-K search is what fails to converge.

THE ESCAPE (brain-grounded, candidate #2 -- the structurally-faithful one):
  THETA-GAMMA SEQUENTIAL RE-ENCODING. The brain never poses the K-way joint-search problem: it holds
  K items in K distinct phase slots (theta-nested gamma sub-cycles) and resolves them ONE-AT-A-TIME.
  Re-encode the K role/filler bindings NOT as a single deep multiplicative product
  s = x_0 * x_1 * ... * x_{K-1} (which requires joint factorization to decode), but as a SLOT
  SUPERPOSITION:
        s_slot = sum_k  r_k (*) x_k                       (r_k = fixed per-slot "gamma carrier")
  where (*) is FHRR multiplicative bind and x_k = book[k][i_k]. Each item now lives in its own slot
  and is recoverable by a single 1-way unbind + cleanup (which the substrate does well at any K),
  with PEEL-OFF / DEFLATION removing each resolved item before the next:
        residual = s_slot
        for k in order:
            probe  = residual (*) conj(r_k)      # unbind slot k -> x_k + crosstalk
            i_k^   = argmax_m Re<book[k][m], probe>
            residual = residual - r_k (*) book[k][i_k^]   # DEFLATE resolved item
  This converts one K-way joint search (M^K config space, non-convergent at K5/K6) into K sequential
  ~1-way searches (K*M total, each convergent). It changes the SEARCH DYNAMICS, not the capacity.

WHAT IS MEASURED per K (PAIRED: identical codebooks + true tuples across all arms):
  - vanilla_oracle_any  : P(true tuple present among R=10 restart candidates) -- reachability CEILING
                          (generous to vanilla: 10 restarts + a perfect oracle verifier). Reproduces
                          the wall in-run: K5/K6 -> 0 while K3/K4 fire (positive control, Gate D).
  - vanilla_verifier    : R=10 verifier-selected exact-match accuracy (what vanilla ACHIEVES).
  - slot_nodeflate_acc  : slot superposition, single-shot per-slot unbind, NO deflation (ablation).
  - slot_peel_acc       : slot superposition, single-shot, sequential peel-off + deflation (THE ESCAPE).
  HEADLINE = slot_peel_acc(K5), slot_peel_acc(K6) vs vanilla_oracle_any(K5)=vanilla_oracle_any(K6)=0.
  NOTE the comparison HANDICAPS the escape: slot_peel is a single deterministic shot (no restarts, no
  oracle verifier); vanilla_oracle_any is the R=10 reachability ceiling with a perfect verifier. If
  slot_peel(1 shot) beats vanilla_oracle(R=10, verifier), the escape wins on an uneven field.

PRE-REG bands (promotion bar set by skunkworks: expansion-INDEPENDENT oracle_any(K5) >= 0.30 PAIRED
vs R10 vanilla, >= 3 seeds; N is IDENTICAL to vanilla -- NO dimensional expansion, so the lift is
expansion-independent by construction):
  HARD-PASS  : slot_peel_acc(K5) >= 0.30 AND slot_peel_acc(K6) >= 0.30 AND vanilla_oracle_any(K5) < 0.10
               (escape rescues BOTH crater-K's against a firing failure). The escape converts the
               K-way joint wall into a benign-capacity slotted readout.
  PARTIAL    : slot_peel_acc(K5) >= 0.30 AND slot_peel_acc(K6) < 0.30 (K5 rescued, K6 not).
  HARD-FAIL  : slot_peel_acc(K5) < 0.30 (escape does NOT rescue even K5) -- honest negative; report
               faithfully. Would mean the slotted re-encoding does not deliver the K-way capability
               where joint factorization fails at this regime.
  Integrity gates precede band classification:
   (G1) POSITIVE CONTROL (Gate D): vanilla reproduces the wall AT TEST REGIME -- K3 oracle in
        [0.95,1.00] (ref 0.992), K4 oracle in [0.72,0.90] (ref 0.806), K5 oracle < 0.10 (ref 0.000).
        MEASURED@data/exp_resonator_ksweep_reachability_v1/metrics.json. If vanilla does NOT reproduce
        the wall, the numpy port diverged / the wall is not firing -> HARD_FAIL (comparison void).
   (G2) EXPANSION-INDEPENDENCE: slot arm uses N == vanilla N == 4096 (NO r*N expansion). Asserted.
   (G3) PEEL-OPERATOR self-test: resolving+removing one factor preserves the remaining K-1 binding
        exactly (deflation invariant). Asserted in _selftest.

baseline_in_band (META_RULE_AG) EXEMPTION: vanilla_oracle_any(K5)=vanilla_oracle_any(K6)=0 is NOT a
saturation/too-easy artifact -- it IS the confirmed firing failure under study (the paired baseline).
Vanilla is in-band at low K (K3~0.99, K4~0.81), proving the harness measures a real K-gradient, not a
constant-zero. The discriminator is the gap slot_peel - vanilla, maximal exactly when vanilla=0.

FAIRNESS / interpretation caveat (pre-registered, do NOT over-claim): the slot arm does NOT make the
vanilla joint resonator converge at K5 -- it SIDESTEPS the joint search by re-encoding. The finding is
"the downstream CAPABILITY (K-way conjunctive binding + full recovery) is deliverable via theta-gamma
slot re-encoding where joint-product factorization is non-convergent," at the cost of additive slot
capacity (benign at K<=6 / N=4096: SNR ~ sqrt(N/(K-1)) ~ 28). Report the re-encoding honestly.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (slot_peel winners != vanilla winners at K5)
# - final_metrics_atomicity: tmp_replace (write_metrics) + per-seed partials
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - discriminator_reachability: bands bracket the escape lift; HP threshold 0.30 reachable
# - positive control at test regime (vanilla reproduces K3/K4/K5 wall; Gate D)
# - discriminator survives scale (smoke at FULL N=4096 M=30 K grid; only TR/seeds reduced)
# - cardinality_ok: EXPECTED_N_UNITS = seeds*K gate
# - PAIRED trials: identical codebooks + true tuples across all arms
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
import os, json, argparse, time, traceback, platform
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "resonator_theta_gamma_peel_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- config (IDENTICAL decode machinery to exp_resonator_ksweep_reachability_v1) ---
N = 4096            # IDENTICAL to vanilla; slot arm uses the SAME N (no r*N expansion -> expansion-independent)
M = 30
MAXIT = 60
R = 10              # vanilla restarts per trial (reachability ceiling); HELD to reproduce the wall
T0_VANILLA = 0.50   # vanilla Glauber temperature = best-T0 from reachability (max oracle_any setting)
K_GRID = [3, 4, 5, 6]     # K3/K4 = positive-control reproducers; K5/K6 = the crater regime
TR = 30 if SMOKE else 120
SEEDS = [3] if SMOKE else [3, 7, 13]   # reuse VET seeds -> directly comparable to reachability

# cardinality gate (META_RULE_H)
EXPECTED_N_UNITS = len(SEEDS) * len(K_GRID)

# vanilla reachability references (MEASURED@data/exp_resonator_ksweep_reachability_v1/metrics.json)
K3_ORACLE_REF, K4_ORACLE_REF = 0.992, 0.806
K3_ORACLE_LO, K3_ORACLE_HI = 0.95, 1.00
K4_ORACLE_LO, K4_ORACLE_HI = 0.72, 0.90
K5_ORACLE_CRATER = 0.10          # vanilla_oracle_any(K5) must be < this to confirm the wall fires

# escape promotion bar (skunkworks-set): expansion-independent slot_peel(K5) >= 0.30 PAIRED
SLOT_PEEL_HP = 0.30              # HARD-PASS floor on slot_peel_acc at K5 (and K6 for full HARD-PASS)


# --- phasor primitives (VERBATIM from reachability cell) ---------------------
def phasor(m: int, d: int, rng: np.random.Generator) -> np.ndarray:
    ang = (rng.random((m, d)) * 2 - 1) * np.pi
    return np.exp(1j * ang)


def _norm(v: np.ndarray) -> np.ndarray:
    return v / (np.abs(v) + 1e-8)


def _recon_score(books: List[np.ndarray], s: np.ndarray, cand: Tuple[int, ...], K: int) -> float:
    """Normalized real inner product between probe s and candidate multiplicative reconstruction."""
    sh = np.ones(N, dtype=np.complex128)
    for k in range(K):
        sh = sh * books[k][cand[k]]
    return float(np.real(np.vdot(s, sh)) / N)


# --- theta-gamma slot re-encoding + sequential peel-off decode ---------------
def slot_encode(books: List[np.ndarray], slots: np.ndarray, trues: np.ndarray, K: int) -> np.ndarray:
    """s_slot = sum_k slots[k] * books[k][trues[:,k]].  Shapes: books[k] (M,N); slots (K,N);
    trues (TR,K). Returns (TR,N) complex superposition (theta cycle with K gamma sub-cycles)."""
    TRn = trues.shape[0]
    S = np.zeros((TRn, N), dtype=np.complex128)
    for k in range(K):
        S += slots[k][None, :] * books[k][trues[:, k]]
    return S


def _slot_score(probe: np.ndarray, book_k: np.ndarray) -> np.ndarray:
    """Cleanup score of probe (TR,N) against codebook book_k (M,N) -> (TR,M) real.
    score[t,m] = Re sum_n conj(book_k[m,n]) probe[t,n]; = N at the matched codeword."""
    return (np.conj(probe) @ book_k.T).real


def slot_decode_nodeflate(S: np.ndarray, books: List[np.ndarray], slots: np.ndarray, K: int) -> np.ndarray:
    """Single-shot per-slot unbind + cleanup, NO deflation (ablation). Returns preds (TR,K)."""
    TRn = S.shape[0]
    preds = np.zeros((TRn, K), dtype=np.int64)
    for k in range(K):
        probe = S * np.conj(slots[k])[None, :]
        preds[:, k] = np.argmax(_slot_score(probe, books[k]), axis=1)
    return preds


def slot_decode_peel(S: np.ndarray, books: List[np.ndarray], slots: np.ndarray, K: int) -> np.ndarray:
    """Sequential peel-off: unbind slot k, resolve, DEFLATE its contribution, continue. Returns (TR,K)."""
    residual = S.copy()
    TRn = S.shape[0]
    preds = np.zeros((TRn, K), dtype=np.int64)
    for k in range(K):
        probe = residual * np.conj(slots[k])[None, :]
        ih = np.argmax(_slot_score(probe, books[k]), axis=1)     # (TR,)
        preds[:, k] = ih
        residual = residual - slots[k][None, :] * books[k][ih]   # DEFLATE resolved item
    return preds


# --- resonator joint decode (VERBATIM port; vanilla arm) ---------------------
def decode_trial(books: List[np.ndarray], true: Tuple[int, ...], K: int,
                 R_: int, T0: float, rng: np.random.Generator) -> List[Tuple[int, ...]]:
    """Run R_ (dithered) coupled alternating-projection trajectories, batched. VERBATIM port."""
    s = np.ones(N, dtype=np.complex128)
    for k in range(K):
        s = s * books[k][true[k]]
    est = [np.tile(_norm(books[k].mean(0)), (R_, 1)) for k in range(K)]
    idxs = np.zeros((R_, K), dtype=np.int64)
    prev = None
    locked = np.zeros(R_, dtype=bool)
    answer = np.full((R_, K), -1, dtype=np.int64)
    denom = max(MAXIT - 1, 1)
    for it in range(MAXIT):
        T = T0 * max(0.0, 1.0 - it / denom)
        for k in range(K):
            others = np.ones((R_, N), dtype=np.complex128)
            for j in range(K):
                if j != k:
                    others = others * est[j]
            rr = s[None, :] * np.conj(others)
            sc = np.conj(rr) @ books[k].T
            newest = sc @ books[k]
            if T > 0.0:
                noise = (rng.standard_normal((R_, N)) + 1j * rng.standard_normal((R_, N))) / np.sqrt(2.0)
                newest = newest + T * noise
            est[k] = _norm(newest)
            idxs[:, k] = np.argmax(sc.real, axis=1)
        if prev is not None:
            agree = np.all(idxs == prev, axis=1) & (~locked)
            if agree.any():
                answer[agree] = idxs[agree]
                locked[agree] = True
        prev = idxs.copy()
    if (~locked).any():
        answer[~locked] = idxs[~locked]
    return [tuple(answer[r].tolist()) for r in range(R_)]


def _hash_int_array(a: np.ndarray) -> str:
    import hashlib
    return hashlib.sha256(np.ascontiguousarray(a.astype(np.int64)).tobytes()).hexdigest()


# --- self-test ---------------------------------------------------------------
def _selftest() -> None:
    import numpy as _n
    # 1. phasor unit modulus
    ang = _n.array([0.0, _n.pi / 2, _n.pi])
    assert _n.allclose(_n.abs(_n.exp(1j * ang)), 1.0), "phasor modulus"
    # 2. vanilla reconstruction verifier: true tuple -> 1.0; wrong -> small (port health)
    rng = _n.random.default_rng(0)
    K = 5
    books = [phasor(M, N, rng) for _ in range(K)]
    true = (7, 3, 19, 2, 11)
    s = _n.ones(N, dtype=_n.complex128)
    for k in range(K):
        s = s * books[k][true[k]]
    assert abs(_recon_score(books, s, true, K) - 1.0) < 1e-9, "verifier exact-match must be 1.0"
    wrong = (7, 3, 19, 2, 5)
    assert abs(_recon_score(books, s, wrong, K)) < 0.2, "verifier wrong-tuple must be small"
    # 3. K=1 decode recovers truth (port health)
    sc1 = _n.conj(books[0][7])[None, :] @ books[0].T
    assert int(_n.argmax(sc1.real)) == 7, "K=1 decode recovers truth"

    # 4. SLOT peel-operator: deflation preserves the remaining K-1 binding EXACTLY (G3).
    slots = phasor(K, N, _n.random.default_rng(123))
    trues = _n.array([[7, 3, 19, 2, 11], [1, 2, 3, 4, 5], [29, 0, 15, 8, 22]], dtype=_n.int64)
    S = slot_encode(books, slots, trues, K)
    # 4a. encoding depends on ALL fillers (flip one filler -> S changes)
    trues2 = trues.copy(); trues2[0, 2] = (trues[0, 2] + 1) % M
    S2 = slot_encode(books, slots, trues2, K)
    assert not _n.allclose(S[0], S2[0]), "slot encoding must depend on every filler"
    # 4b. single-shot per-slot unbind recovers every factor (1-way cleanup works at K5/N=4096)
    pred_nd = slot_decode_nodeflate(S, books, slots, K)
    assert _n.array_equal(pred_nd, trues), "slot nodeflate must recover all K per slot: %s" % pred_nd.tolist()
    # 4c. peel recovers the exact true tuple
    pred_pl = slot_decode_peel(S, books, slots, K)
    assert _n.array_equal(pred_pl, trues), "slot peel must recover exact true tuple: %s" % pred_pl.tolist()
    # 4d. DEFLATION INVARIANT: after resolving+removing factor 0 (correctly), residual == sum_{k>=1} r_k*x_k
    residual = S[0].copy()
    probe0 = residual * _n.conj(slots[0])
    ih0 = int(_n.argmax(_slot_score(probe0[None, :], books[0])[0]))
    assert ih0 == int(trues[0, 0]), "peel step-0 must resolve factor 0"
    residual = residual - slots[0] * books[0][ih0]
    remaining = _n.zeros(N, dtype=_n.complex128)
    for k in range(1, K):
        remaining += slots[k] * books[k][int(trues[0, k])]
    assert _n.allclose(residual, remaining, atol=1e-9), \
        "DEFLATION INVARIANT violated: residual != clean (K-1)-slot superposition (max err %.2e)" \
        % float(_n.max(_n.abs(residual - remaining)))
    # 4e. and the peeled residual then still decodes the remaining K-1 exactly (binding preserved)
    pred_rem = slot_decode_peel(residual[None, :], books, slots, K)  # slot 0 already gone -> resolves to argmax noise
    for k in range(1, K):
        assert pred_rem[0, k] == int(trues[0, k]), "post-deflation remaining binding must decode factor %d" % k

    # 5. EXPANSION-INDEPENDENCE (G2): slot arm dimensionality == vanilla N (no r*N expansion)
    assert S.shape[1] == N == books[0].shape[1], "expansion-independence: slot N must equal vanilla N=%d" % N

    print("[selftest] PASS: resonator-theta-gamma-peel (5 groups; peel deflation-invariant, "
          "slot recovers K=%d at N=%d, expansion-independent)" % (K, N), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# --- defensive instrumentation (mirror reachability cell) --------------------
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
    """All K arms for one seed. PAIRED: same codebooks + true tuples across vanilla + slot arms."""
    out: Dict[str, Dict] = {}
    arms_hashes: Dict[str, str] = {}
    unit = unit_base
    for K in K_GRID:
        # PAIRED codebooks + true tuples (SAME derivation as reachability -> vanilla reproduces the wall)
        rng_book = np.random.default_rng(seed * 100 + K)
        books = [phasor(M, N, rng_book) for _ in range(K)]
        rng_trial = np.random.default_rng(seed * 1000 + K)
        trues_list = [tuple(int(x) for x in rng_trial.integers(0, M, size=K)) for _ in range(TR)]
        trues = np.array(trues_list, dtype=np.int64)                 # (TR,K)
        # theta-gamma slot carriers (fixed per seed+K; distinct rng stream)
        slots = phasor(K, N, np.random.default_rng(seed * 7777 + K))

        # --- vanilla arm: joint resonator, R=10, T0=0.50 (reachability ceiling + achieved verifier) ---
        rng_dither = np.random.default_rng(seed * 100003 + K * 1009 + int(round(T0_VANILLA * 1000)))
        v_oracle = 0
        v_verifier = 0
        v_winners = np.zeros((TR, K), dtype=np.int64)
        for ti, true in enumerate(trues_list):
            tuples = decode_trial(books, true, K, R_=R, T0=T0_VANILLA, rng=rng_dither)
            s = np.ones(N, dtype=np.complex128)
            for k in range(K):
                s = s * books[k][true[k]]
            uniq = list(set(tuples))
            v_oracle += int(any(t == true for t in tuples))
            ver_winner = max(uniq, key=lambda c: _recon_score(books, s, c, K))
            v_verifier += int(ver_winner == true)
            v_winners[ti] = np.array(ver_winner, dtype=np.int64)

        # --- slot arms: single-shot re-encoding decode (the escape + its ablation) ---
        S = slot_encode(books, slots, trues, K)
        pred_nd = slot_decode_nodeflate(S, books, slots, K)
        pred_pl = slot_decode_peel(S, books, slots, K)
        acc_nd = float(np.mean(np.all(pred_nd == trues, axis=1)))
        acc_pl = float(np.mean(np.all(pred_pl == trues, axis=1)))

        out["K%d" % K] = {
            "vanilla_oracle_any": v_oracle / TR,
            "vanilla_verifier": v_verifier / TR,
            "slot_nodeflate_acc": acc_nd,
            "slot_peel_acc": acc_pl,
            "K": K, "R": R, "T0_vanilla": T0_VANILLA, "TR": TR,
        }
        arms_hashes["K%d_vanilla" % K] = _hash_int_array(v_winners)
        arms_hashes["K%d_slot_peel" % K] = _hash_int_array(pred_pl)
        arms_hashes["K%d_slot_nodeflate" % K] = _hash_int_array(pred_nd)

        unit += 1
        _heartbeat(output_dir, unit, total_units, t0_start,
                   {"seed": seed, "K": K, "vanilla_oracle_any": v_oracle / TR,
                    "slot_peel_acc": acc_pl})
        print("  seed=%d K=%d vanilla_oracle=%.3f vanilla_ver=%.3f slot_nodeflate=%.3f slot_peel=%.3f" %
              (seed, K, v_oracle / TR, v_verifier / TR, acc_nd, acc_pl), flush=True)

    return {"seed": seed, "by_arm": out, "arms_hashes": arms_hashes,
            "N": N, "M": M, "run_mode": RUN_MODE}


# --- verdict -----------------------------------------------------------------
def _mean_over_seeds(per_seed: List[Dict], K: int, field: str) -> float:
    return float(np.mean([ps["by_arm"]["K%d" % K][field] for ps in per_seed]))


def build_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    traj: Dict[str, Dict] = {}
    for K in K_GRID:
        traj[str(K)] = {
            "vanilla_oracle_any": _mean_over_seeds(per_seed, K, "vanilla_oracle_any"),
            "vanilla_verifier": _mean_over_seeds(per_seed, K, "vanilla_verifier"),
            "slot_nodeflate_acc": _mean_over_seeds(per_seed, K, "slot_nodeflate_acc"),
            "slot_peel_acc": _mean_over_seeds(per_seed, K, "slot_peel_acc"),
        }
    detail = {"trajectory": traj,
              "bands": {"slot_peel_hp": SLOT_PEEL_HP, "k5_oracle_crater": K5_ORACLE_CRATER,
                        "k3_band": [K3_ORACLE_LO, K3_ORACLE_HI], "k4_band": [K4_ORACLE_LO, K4_ORACLE_HI]}}

    o3 = traj["3"]["vanilla_oracle_any"]; o4 = traj["4"]["vanilla_oracle_any"]; o5 = traj["5"]["vanilla_oracle_any"]
    p5 = traj["5"]["slot_peel_acc"]; p6 = traj["6"]["slot_peel_acc"]

    pc_k3 = K3_ORACLE_LO <= o3 <= K3_ORACLE_HI
    pc_k4 = K4_ORACLE_LO <= o4 <= K4_ORACLE_HI
    pc_k5 = o5 < K5_ORACLE_CRATER
    detail["positive_control"] = {"K3_oracle": o3, "K3_ok": bool(pc_k3),
                                  "K4_oracle": o4, "K4_ok": bool(pc_k4),
                                  "K5_oracle": o5, "K5_wall_fires": bool(pc_k5)}
    detail["positive_control_ok"] = bool(pc_k3 and pc_k4 and pc_k5)

    traj_str = " ".join("K%d(van_orc=%.3f,peel=%.3f)" %
                        (K, traj[str(K)]["vanilla_oracle_any"], traj[str(K)]["slot_peel_acc"])
                        for K in K_GRID)

    # Gate G1: positive control -- vanilla must reproduce the wall at test regime
    if not detail["positive_control_ok"]:
        return ("HARD_FAIL",
                "HARD_FAIL_POSITIVE_CONTROL (Gate D): vanilla did NOT reproduce the wall at test regime -- "
                "K3 oracle=%.3f (need [%.2f,%.2f]) K4=%.3f (need [%.2f,%.2f]) K5=%.3f (need <%.2f). "
                "Comparison VOID (port diverged or wall not firing). traj: %s"
                % (o3, K3_ORACLE_LO, K3_ORACLE_HI, o4, K4_ORACLE_LO, K4_ORACLE_HI, o5, K5_ORACLE_CRATER, traj_str),
                detail)

    # Gate G2/G3 (expansion-independence + peel invariant) enforced in _selftest at import; re-affirm flag
    detail["expansion_independent"] = True  # slot N == vanilla N == 4096 (asserted in _selftest)

    # band classification on slot_peel vs a firing vanilla failure
    if p5 >= SLOT_PEEL_HP and p6 >= SLOT_PEEL_HP:
        return ("HARD_PASS",
                "ESCAPE_CONFIRMED (HARD_PASS): theta-gamma slot peel rescues BOTH crater-K's -- "
                "slot_peel(K5)=%.3f slot_peel(K6)=%.3f >= %.2f while vanilla_oracle_any(K5)=%.3f (R=10 ceiling, "
                "verifier-generous) fires the wall. Expansion-independent (N=%d, no expansion). The K-way "
                "joint-factorization wall is ESCAPABLE by sequential phase-slot re-encoding + peel-off "
                "deflation; SEARCH DYNAMICS changed, not capacity. traj: %s"
                % (p5, p6, SLOT_PEEL_HP, o5, N, traj_str), detail)

    if p5 >= SLOT_PEEL_HP:
        return ("PARTIAL",
                "PARTIAL: theta-gamma slot peel rescues K5 (slot_peel=%.3f >= %.2f) but NOT K6 (slot_peel=%.3f "
                "< %.2f) against vanilla_oracle_any(K5)=%.3f. Escape works at K5; K6 needs more (deeper slotting "
                "or higher precision). traj: %s"
                % (p5, SLOT_PEEL_HP, p6, SLOT_PEEL_HP, o5, traj_str), detail)

    return ("HARD_FAIL",
            "HARD_FAIL_NO_RESCUE: theta-gamma slot peel does NOT rescue even K5 (slot_peel=%.3f < %.2f) "
            "against vanilla_oracle_any(K5)=%.3f. Honest negative: slotted re-encoding does not deliver the "
            "K-way capability where joint factorization fails at this regime. traj: %s"
            % (p5, SLOT_PEEL_HP, o5, traj_str), detail)


def main() -> None:
    output_dir = get_output_dir(ANCHOR_NAME)
    total_units = EXPECTED_N_UNITS
    _write_start_marker(output_dir, total_units)
    print("[config] anchor=%s mode=%s N=%d M=%d MAXIT=%d R=%d T0v=%.2f TR=%d K=%s seeds=%s expected_units=%d" %
          (ANCHOR_NAME, RUN_MODE, N, M, MAXIT, R, T0_VANILLA, TR, K_GRID, SEEDS, total_units), flush=True)

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

    # ARMS-MUST-DIFFER (META_RULE_AF): slot_peel winners must differ from vanilla winners at K5
    ref = per_seed[0]["arms_hashes"]
    arms_differ_ok = ref.get("K5_slot_peel") != ref.get("K5_vanilla")
    if not arms_differ_ok:
        raise RuntimeError("META_RULE_AF VIOLATION: slot_peel and vanilla produced bit-identical winners at "
                           "K5 -- the escape had zero effect (implementation bug or both cratered identically)")

    verdict, vmsg, detail = build_verdict(per_seed)
    detail["arms_differ_verified"] = bool(arms_differ_ok)

    # SMOKE DISCRIMINATOR-FIRES: the escape lift must fire AND the vanilla wall must reproduce
    traj = detail["trajectory"]
    lift_k5 = traj["5"]["slot_peel_acc"] - traj["5"]["vanilla_oracle_any"]
    vanilla_declines = traj["5"]["vanilla_oracle_any"] < traj["3"]["vanilla_oracle_any"]
    detail["smoke_escape_lift_k5"] = lift_k5
    detail["smoke_vanilla_declines"] = bool(vanilla_declines)
    detail["smoke_discriminator_fired"] = bool(lift_k5 >= SLOT_PEEL_HP and vanilla_declines)
    if SMOKE and not detail["smoke_discriminator_fired"]:
        print("[SMOKE_GATE_FAIL] discriminator did NOT fire: escape lift(K5)=%.3f (need>=%.2f) "
              "vanilla_declines=%s. DO NOT dispatch FULL." % (lift_k5, SLOT_PEEL_HP, vanilla_declines), flush=True)

    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "per_seed": per_seed, "detail": detail,
        "config": {"N": N, "M": M, "MAXIT": MAXIT, "R": R, "T0_VANILLA": T0_VANILLA,
                   "TR": TR, "K_GRID": K_GRID, "SEEDS": SEEDS, "EXPECTED_N_UNITS": EXPECTED_N_UNITS},
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
