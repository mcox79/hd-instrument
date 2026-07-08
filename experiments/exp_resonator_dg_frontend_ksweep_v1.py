"""
exp_resonator_dg_frontend_ksweep_v1.py -- DG-front-end DIMENSIONAL-EXPANSION escape from the
resonator K5/K6 capacity wall (5x-drill #1 on a skunkworks-confirmed genuine negative). GPU.

RESEARCH CONTEXT (notes/research_brain_grounding_resonator_basin_proliferation_2026-07-08.md
candidate #1; gated on exp_resonator_dg_crosstalk_disentangler_v1 = GATE_CLEAR_EXPANSION):
The vanilla resonator craters at K5/K6 (oracle_any=0, all seeds) at N=4096, M=30
(MEASURED@data/exp_resonator_ksweep_reachability_v1*/metrics.json). Skunkworks-confirmed genuine;
diagnosed as a CONFIG-CONTINGENT CROSSTALK/SNR CAPACITY CLIFF (wall at M^K ~ N^2, Tsodyks-Feigelman
crosstalk-noise), NOT fundamental basin-multiplicity. It MOVES with N. The escape LEVER = DIMENSIONAL
EXPANSION (raise effective N via r*N so crosstalk SNR ~ sqrt(N) rises), the mechanistically-supported
half of the dentate-gyrus DGProjection primitive.

CPU DISENTANGLER PRE-CHECK (already landed, GATE_CLEAR):
  MEASURED@data/exp_resonator_dg_crosstalk_disentangler_v1/metrics.json:
  - expansion 4096->16384 lowers ORACLE-unbind crosstalk_std 0.0106->0.0054 (1.96x ~ sqrt(4)) and
    raises margin 0.977->0.989 => expansion is a real crosstalk lever (Tsodyks-Feigelman confirmed).
  - DG decorrelation ports to complex FHRR (gap=0.272 >= 0.15).
  - naive top-K sparsify (0.02) COLLAPSES the K-way binding support (oracle margin 0.002, recover 0.00)
    => sparsify arm is EXPECTED-TO-CRATER; the rescue rides on expansion-ALONE.

THREE PAIRED ARMS (identical true tuples + matched-seed codebooks within each (seed, K)):
  - vanilla   : dense phasor codebooks at N=4096  (reproduces the wall; positive control @ K3/K4)
  - expansion : dense phasor codebooks at N=16384 (r=4)  -- THE mechanistically-supported rescue
  - sparsify  : DG-analog sparse-phasor codebooks at N=16384 (top-2%)  -- informative-crater ablation
The decode (Glauber-dither + R-restart alternating projection + oracle_any reachability) is a torch
port of the IDENTICAL instrument used by exp_resonator_ksweep_reachability_v1 / _verifier_readout_v1
(verbatim math; batched over trials x restarts for GPU). oracle_any = reachability (any of R restarts
lands the true tuple). Verifier read-out kept for parity.

CAPACITY MATH (THEORETICAL@ M^K vs N^2 crosstalk wall):
  r=4 (N 4096->16384) drops K5 ratio M^5/N^2  1.45 -> 0.091  (SHOULD rescue K5)
  r=4                 drops K6 ratio M^6/N^2  43.5 -> 2.72   (>1; likely NOT rescued => modal=PARTIAL)

PRE-REG bands (3-band; judged on the EXPANSION arm oracle_any, paired vs vanilla; per research note (b)
and the coordinator's honest-band directive -- PARTIAL is its OWN informative outcome, NOT a fail):
  HARD_PASS (both K5 AND K6 rescued): oracle_any_exp(K5) >= 0.70 AND oracle_any_exp(K6) >= 0.40.
  PARTIAL_RESCUE (K5 rescued only -- the capacity-math MODAL prediction): oracle_any_exp(K5) >= 0.70
             AND oracle_any_exp(K6) < 0.40. Informative: expansion rescues K5 as predicted; K6 stays
             above the M^K~N^2 wall at r=4 (would need larger r).
  HARD_FAIL (neither rescued): oracle_any_exp(K5) < 0.70 -- expansion lowered ORACLE crosstalk (proven
             in disentangler) but did NOT move BASIN reachability; would sharpen the basin-count-vs-
             crosstalk distinction (crosstalk fell yet reachability did not recover).

POSITIVE CONTROL (Gate D -- reproduce prior at test regime): vanilla arm K3 oracle_any in [0.95,1.00]
  (ref 0.992), K4 in [0.72,0.90] (ref 0.806), both MEASURED@data/exp_resonator_verifier_readout_v1.
DISCRIMINATOR-FIRES: vanilla arm MUST crater at K5 (oracle_any_vanilla(K5) < 0.30, reproducing the
  confirmed negative) AND expansion arm must be measured paired against it -- else the wall was not
  reproduced and the sweep is vacuous (HARD_FAIL_POSITIVE_CONTROL).
INVARIANT: verifier success <= oracle_any per arm (verifier can only pick from the R candidates).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (vanilla vs expansion vs sparsify codebook/reachability hashes)
# - final_metrics_atomicity: tmp_replace (write_metrics) + per-seed partials
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - discriminator_reachability: bands bracket capacity-math (K5 ratio 0.091 => reachable) at r=4
# - baseline_in_band / positive-control at smoke (K3/K4 reproduce; K5 vanilla craters; Gate D)
# - discriminator survives scale: smoke at reduced N with vanilla-craters + expansion-lifts;
#   FULL analytical justification via M^K/N^2 ratios (option B)
# - cardinality_ok: EXPECTED_N_UNITS = seeds * K * arms
# - PAIRED trials: identical codebooks + true tuples across arms
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
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import json, argparse, time, math, hashlib, traceback, platform
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

ANCHOR_NAME = "resonator_dg_frontend_ksweep_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- config -----------------------------------------------------------------
M = 30
R_EXPAND = 4
MAXIT = 40 if SMOKE else 60
R = 10                              # restarts per trial (held == confirmed-negative harness)
T0_GRID = [0.20, 0.35, 0.50]       # dither temps (>0; best-oracle picked over these)
SPARSITY = 0.02
if SMOKE:
    # env-parametrized for discriminator-survives-scale checks (defaults: N_base=2048 -> expansion 8192).
    # HDLAB_SMOKE_NBASE / HDLAB_SMOKE_KGRID let a targeted CPU preview probe the FULL's actual N=16384.
    N_BASE = int(os.environ.get("HDLAB_SMOKE_NBASE", "2048"))
    _kg = os.environ.get("HDLAB_SMOKE_KGRID", "").strip()
    K_GRID = [int(x) for x in _kg.split(",")] if _kg else [4, 5, 6]
    TR = int(os.environ.get("HDLAB_SMOKE_TR", "24"))
    SEEDS = [int(x) for x in os.environ.get("HDLAB_SMOKE_SEEDS", "3").split(",")]
    TRIAL_CHUNK = 24
else:
    N_BASE = 4096                  # confirmed-negative regime
    K_GRID = [3, 4, 5, 6]          # K3/K4 positive controls; K5/K6 probe
    TR = 120
    SEEDS = [3, 7, 13]
    TRIAL_CHUNK = 40
N_EXP = N_BASE * R_EXPAND
ARMS = ["vanilla", "expansion", "sparsify"]
ARM_N = {"vanilla": N_BASE, "expansion": N_EXP, "sparsify": N_EXP}

EXPECTED_N_UNITS = len(SEEDS) * len(K_GRID) * len(ARMS)

# reachability references (MEASURED@data/exp_resonator_verifier_readout_v1/metrics.json best-T0)
K3_ORACLE_LO, K3_ORACLE_HI = 0.95, 1.00
K4_ORACLE_LO, K4_ORACLE_HI = 0.72, 0.90
# 3-band thresholds on the EXPANSION arm
HP_K5, HP_K6 = 0.70, 0.40
VANILLA_CRATER_CEIL = 0.30         # vanilla K5 must be below this (wall reproduced)


def _selftest() -> None:
    # capacity-math anchors (THEORETICAL M^K/N^2)
    r5_base = (M ** 5) / (4096 ** 2)
    r5_exp = (M ** 5) / (16384 ** 2)
    r6_exp = (M ** 6) / (16384 ** 2)
    assert abs(r5_base - 1.4485) < 0.01, "K5 base ratio %.4f" % r5_base
    assert abs(r5_exp - 0.0905) < 0.005, "K5 exp ratio %.4f" % r5_exp
    assert r6_exp > 1.0, "K6 exp ratio %.3f must exceed 1 (partial prediction)" % r6_exp
    # decode-math sanity in numpy (mirror of the torch port): oracle unbind recovers K=1 truth
    import numpy as _n
    rng = _n.random.default_rng(0)
    b = _n.exp(1j * (rng.random((M, 512)) * 2 - 1) * _n.pi)
    s1 = b[7]
    sc = _n.real(_n.conj(s1)[None, :] @ b.T)
    assert int(_n.argmax(sc)) == 7, "K=1 decode recovers truth"
    # sparse-phasor generator sparsity target
    z = rng.standard_normal((3, 4096)) + 1j * rng.standard_normal((3, 4096))
    mag = _n.abs(z); k = max(1, int(round(0.02 * 4096)))
    thr = _n.partition(mag, 4096 - k, axis=1)[:, 4096 - k][:, None]
    rate = float(_n.count_nonzero(mag >= thr)) / mag.size
    assert 0.015 <= rate <= 0.030, "sparse rate %.4f" % rate
    print("[selftest] PASS: resonator-dg-frontend-ksweep (K5 ratio base=%.3f exp=%.3f K6 exp=%.2f; "
          "decode+sparse ok)" % (r5_base, r5_exp, r6_exp), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

# --- torch device -----------------------------------------------------------
try:
    import torch
except Exception as e:
    print("[FATAL] torch import: %s" % e, flush=True)
    sys.exit(1)
if torch.cuda.is_available():
    DEV = torch.device("cuda")
    print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
else:
    if not SMOKE and os.environ.get("HDLAB_ALLOW_CPU_FULL", "0") != "1":
        print("[FATAL] FULL run requires CUDA (set HDLAB_ALLOW_CPU_FULL=1 to override for debugging).",
              flush=True)
        sys.exit(1)
    DEV = torch.device("cpu")
    print("[CPU] no CUDA; running on CPU (mode=%s)" % RUN_MODE, flush=True)
CDT = torch.complex64


# --- codebooks --------------------------------------------------------------
def phasor_dense(m: int, d: int, g: torch.Generator) -> torch.Tensor:
    ang = (torch.rand(m, d, generator=g, device=DEV) * 2 - 1) * math.pi
    return torch.complex(torch.cos(ang), torch.sin(ang)).to(CDT)


def phasor_sparse(m: int, d: int, sparsity: float, g: torch.Generator) -> torch.Tensor:
    """DG-analog: complex-gaussian -> top-K by |z| -> unit-phase survivors, zeros elsewhere."""
    zr = torch.randn(m, d, generator=g, device=DEV)
    zi = torch.randn(m, d, generator=g, device=DEV)
    mag = torch.sqrt(zr * zr + zi * zi)
    k = max(1, int(round(sparsity * d)))
    thresh = torch.kthvalue(mag, d - k + 1, dim=1, keepdim=True).values
    mask = (mag >= thresh).to(torch.float32)
    phase = torch.complex(zr, zi) / (mag + 1e-12)
    return (phase * mask).to(CDT)


def _norm_t(v: torch.Tensor) -> torch.Tensor:
    return v / (v.abs() + 1e-8)


def _bound(books: List[torch.Tensor], trues: torch.Tensor, K: int, N: int) -> torch.Tensor:
    """Bound product per trial. trues:(C,K) long -> s:(C,N) complex."""
    C = trues.shape[0]
    s = torch.ones((C, N), dtype=CDT, device=DEV)
    for k in range(K):
        s = s * books[k][trues[:, k]]
    return s


def decode_batch(books: List[torch.Tensor], trues: torch.Tensor, K: int, N: int,
                 R_: int, T0: float, g: torch.Generator) -> torch.Tensor:
    """Batched Glauber-dither R-restart alternating projection. Returns answer (C, R_, K) long (cpu).
    VERBATIM math port of exp_resonator_ksweep_reachability_v1.decode_trial, batched over trials*restarts."""
    C = trues.shape[0]
    B = C * R_
    s = _bound(books, trues, K, N).repeat_interleave(R_, dim=0)   # (B,N)
    est = [_norm_t(books[k].mean(0)).unsqueeze(0).expand(B, N).clone() for k in range(K)]
    idxs = torch.zeros((B, K), dtype=torch.int64, device=DEV)
    prev = None
    locked = torch.zeros(B, dtype=torch.bool, device=DEV)
    answer = torch.full((B, K), -1, dtype=torch.int64, device=DEV)
    denom = max(MAXIT - 1, 1)
    for it in range(MAXIT):
        T = T0 * max(0.0, 1.0 - it / denom)
        for k in range(K):
            others = torch.ones((B, N), dtype=CDT, device=DEV)
            for j in range(K):
                if j != k:
                    others = others * est[j]
            rr = s * others.conj()                       # (B,N)
            sc = rr.conj() @ books[k].T                  # (B,M)
            newest = sc @ books[k]                       # (B,N)
            if T > 0.0:
                nr = torch.randn(B, N, generator=g, device=DEV)
                ni = torch.randn(B, N, generator=g, device=DEV)
                newest = newest + T * torch.complex(nr, ni).to(CDT) / math.sqrt(2.0)
            est[k] = _norm_t(newest)
            idxs[:, k] = torch.argmax(sc.real, dim=1)
        if prev is not None:
            agree = (idxs == prev).all(dim=1) & (~locked)
            if agree.any():
                answer[agree] = idxs[agree]
                locked[agree] = True
        prev = idxs.clone()
    if (~locked).any():
        answer[~locked] = idxs[~locked]
    return answer.view(C, R_, K).cpu()


def _recon_score(books_np: List[np.ndarray], s_np: np.ndarray, cand: Tuple[int, ...],
                 K: int, N: int) -> float:
    sh = np.ones(N, dtype=np.complex128)
    for k in range(K):
        sh = sh * books_np[k][cand[k]]
    return float(np.real(np.vdot(s_np, sh)) / N)


def _hash_tuples(tuples: List[Tuple[int, ...]]) -> str:
    b = json.dumps(sorted(tuples), sort_keys=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def _write_start_marker(output_dir: Path, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": expected_n_units, "host": platform.node()}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total: int, t0: float, extra: Dict) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total, "elapsed_s": time.perf_counter() - t0}
    row.update(extra)
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")


def run_arm(arm: str, K: int, seed: int, output_dir: Path, t0: float,
            unit_idx: int, total: int) -> Dict:
    """One (arm, K, seed). PAIRED: same true tuples across arms (seeded by seed*K, arm-independent)."""
    N = ARM_N[arm]
    g_book = torch.Generator(device=DEV).manual_seed(seed * 100000 + K * 97 + hash(arm) % 997)
    if arm == "sparsify":
        books = [phasor_sparse(M, N, SPARSITY, g_book) for _ in range(K)]
    else:
        books = [phasor_dense(M, N, g_book) for _ in range(K)]
    # PAIRED true tuples: identical index tuples across arms (arm-independent rng)
    rng_t = np.random.default_rng(seed * 1000 + K)
    trues_np = rng_t.integers(0, M, size=(TR, K)).astype(np.int64)
    trues = torch.from_numpy(trues_np).to(DEV)

    g_dith = torch.Generator(device=DEV).manual_seed(seed * 100003 + K * 1009 + hash(arm) % 991)
    books_np = [b.detach().cpu().numpy().astype(np.complex128) for b in books]

    best = {"oracle_any": -1.0, "verifier": 0.0, "plurality": 0.0, "T0": None,
            "ver_le_oracle_viol": 0}
    reach_sig: List[Tuple[int, ...]] = []
    for T0 in T0_GRID:
        oracle_hits = 0
        ver_hits = 0
        plur_hits = 0
        ver_le_oracle_viol = 0
        winners: List[Tuple[int, ...]] = []
        for c0 in range(0, TR, TRIAL_CHUNK):
            c1 = min(c0 + TRIAL_CHUNK, TR)
            ans = decode_batch(books, trues[c0:c1], K, N, R, T0, g_dith)  # (C,R,K)
            for ci in range(c1 - c0):
                true_t = tuple(int(x) for x in trues_np[c0 + ci])
                cands = [tuple(int(x) for x in ans[ci, r]) for r in range(R)]
                truth_present = any(t == true_t for t in cands)
                oracle_hits += int(truth_present)
                plur_winner = Counter(cands).most_common(1)[0][0]
                plur_hits += int(plur_winner == true_t)
                s_np = np.ones(N, dtype=np.complex128)
                for k in range(K):
                    s_np = s_np * books_np[k][true_t[k]]
                uniq = list(set(cands))
                ver_winner = max(uniq, key=lambda cc: _recon_score(books_np, s_np, cc, K, N))
                ver_hit = int(ver_winner == true_t)
                ver_hits += ver_hit
                if ver_hit and not truth_present:
                    ver_le_oracle_viol += 1
                winners.append(ver_winner)
        oracle_any = oracle_hits / TR
        if oracle_any > best["oracle_any"]:
            best = {"oracle_any": oracle_any, "verifier": ver_hits / TR, "plurality": plur_hits / TR,
                    "T0": T0, "ver_le_oracle_viol": ver_le_oracle_viol}
            reach_sig = winners
    _heartbeat(output_dir, unit_idx, total, t0,
               {"arm": arm, "K": K, "seed": seed, "N": N,
                "oracle_any": best["oracle_any"], "verifier": best["verifier"]})
    print("  seed=%d arm=%-9s K=%d N=%5d | oracle_any=%.3f verifier=%.3f plurality=%.3f (bestT0=%.2f)"
          % (seed, arm, K, N, best["oracle_any"], best["verifier"], best["plurality"], best["T0"]),
          flush=True)
    return {"arm": arm, "K": K, "seed": seed, "N": N,
            "oracle_any": best["oracle_any"], "verifier": best["verifier"],
            "plurality": best["plurality"], "best_T0": best["T0"],
            "ver_le_oracle_viol": best["ver_le_oracle_viol"],
            "reach_hash": _hash_tuples(reach_sig)}


def run_seed(seed: int, output_dir: Path, t0: float, unit_base: int, total: int) -> Dict:
    by: Dict[str, Dict] = {}
    hashes: Dict[str, str] = {}
    u = unit_base
    for K in K_GRID:
        for arm in ARMS:
            res = run_arm(arm, K, seed, output_dir, t0, u, total)
            key = "%s_K%d" % (arm, K)
            by[key] = res
            hashes[key] = res["reach_hash"]
            u += 1
    return {"seed": seed, "by": by, "hashes": hashes, "run_mode": RUN_MODE,
            "config_version": "ANCHOR=%s,Nbase=%d,Nexp=%d,M=%d" % (ANCHOR_NAME, N_BASE, N_EXP, M)}


def _agg(per_seed: List[Dict], arm: str, K: int, field: str) -> float:
    return float(np.mean([ps["by"]["%s_K%d" % (arm, K)][field] for ps in per_seed]))


def build_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    # integrity: verifier <= oracle invariant
    inv_viol = sum(int(v.get("ver_le_oracle_viol", 0)) for ps in per_seed for v in ps["by"].values())

    orc = {arm: {K: _agg(per_seed, arm, K, "oracle_any") for K in K_GRID} for arm in ARMS}
    detail = {
        "oracle_any": {arm: {str(K): orc[arm][K] for K in K_GRID} for arm in ARMS},
        "verifier": {arm: {str(K): _agg(per_seed, arm, K, "verifier") for K in K_GRID} for arm in ARMS},
        "plurality": {arm: {str(K): _agg(per_seed, arm, K, "plurality") for K in K_GRID} for arm in ARMS},
        "invariant_violations": inv_viol,
        "bands": {"HP_K5": HP_K5, "HP_K6": HP_K6, "vanilla_crater_ceil": VANILLA_CRATER_CEIL,
                  "K3_band": [K3_ORACLE_LO, K3_ORACLE_HI], "K4_band": [K4_ORACLE_LO, K4_ORACLE_HI]},
        "capacity_math": {"K5_ratio_base": (M ** 5) / (N_BASE ** 2), "K5_ratio_exp": (M ** 5) / (N_EXP ** 2),
                          "K6_ratio_exp": (M ** 6) / (N_EXP ** 2)},
    }

    # ARMS-MUST-DIFFER (META_RULE_AF): reachability signatures differ across arms at K5
    k5 = 5 if 5 in K_GRID else K_GRID[-1]
    sigs = {arm: per_seed[0]["hashes"]["%s_K%d" % (arm, k5)] for arm in ARMS}
    arms_differ_ok = len(set(sigs.values())) == len(ARMS)
    detail["arms_differ_verified"] = arms_differ_ok

    o_exp_k5 = orc["expansion"][k5]
    k6 = 6 if 6 in K_GRID else K_GRID[-1]
    o_exp_k6 = orc["expansion"][k6]
    o_van_k5 = orc["vanilla"][k5]
    o_spr_k5 = orc["sparsify"][k5]
    detail["sparsify_crater_confirmed"] = bool(o_spr_k5 < 0.30)

    def s(arm):
        return " ".join("K%d=%.3f" % (K, orc[arm][K]) for K in K_GRID)
    traj = "vanilla[%s] expansion[%s] sparsify[%s]" % (s("vanilla"), s("expansion"), s("sparsify"))

    if inv_viol > 0:
        return ("HARD_FAIL", "HARD_FAIL_INVARIANT: %d verifier>oracle violations (read-out bug). %s"
                % (inv_viol, traj), detail)
    if not arms_differ_ok:
        return ("HARD_FAIL", "META_RULE_AF: arms produced bit-identical reachability at K%d %s -- bug. %s"
                % (k5, sigs, traj), detail)

    # positive control (Gate D) on vanilla arm at test regime
    if 3 in K_GRID:
        o3 = orc["vanilla"][3]
        o4 = orc["vanilla"][4]
        pc_ok = (K3_ORACLE_LO <= o3 <= K3_ORACLE_HI) and (K4_ORACLE_LO <= o4 <= K4_ORACLE_HI)
        detail["positive_control"] = {"K3": o3, "K4": o4, "ok": bool(pc_ok)}
        if not pc_ok:
            return ("HARD_FAIL",
                    "HARD_FAIL_POSITIVE_CONTROL: vanilla K3=%.3f (need [%.2f,%.2f]) K4=%.3f (need [%.2f,%.2f]) "
                    "-- torch port diverged; K5/K6 UNTRUSTED (Gate D). %s"
                    % (o3, K3_ORACLE_LO, K3_ORACLE_HI, o4, K4_ORACLE_LO, K4_ORACLE_HI, traj), detail)

    # discriminator-fires: vanilla must crater at K5 (wall reproduced)
    if o_van_k5 >= VANILLA_CRATER_CEIL:
        return ("HARD_FAIL",
                "HARD_FAIL_DISCRIMINATOR_VACUOUS: vanilla K%d oracle_any=%.3f >= %.2f -- the wall was NOT "
                "reproduced at this regime, so expansion has nothing to rescue (sweep vacuous). %s"
                % (k5, o_van_k5, VANILLA_CRATER_CEIL, traj), detail)

    # 3-band on the expansion arm (paired vs cratered vanilla)
    if o_exp_k5 >= HP_K5 and o_exp_k6 >= HP_K6:
        return ("HARD_PASS",
                "HARD_PASS: expansion (r=%d, N=%d) rescues BOTH K%d (oracle_any=%.3f >= %.2f) and K%d "
                "(%.3f >= %.2f) from cratered vanilla (K%d=%.3f). Dimensional expansion escapes the "
                "crosstalk wall; DG front-end is load-bearing. sparsify-arm crater=%s. %s"
                % (R_EXPAND, N_EXP, k5, o_exp_k5, HP_K5, k6, o_exp_k6, HP_K6, k5, o_van_k5,
                   detail["sparsify_crater_confirmed"], traj), detail)
    if o_exp_k5 >= HP_K5 and o_exp_k6 < HP_K6:
        return ("PARTIAL_RESCUE",
                "PARTIAL_RESCUE (informative, NOT fail): expansion rescues K%d (oracle_any=%.3f >= %.2f) as "
                "the capacity-math MODAL prediction (K5 ratio -> %.3f), but K%d stays low (%.3f < %.2f; K6 "
                "ratio -> %.2f still > 1 at r=%d -- needs larger r). Vanilla cratered K%d=%.3f. Expansion is "
                "a real, partial escape lever. sparsify-arm crater=%s. %s"
                % (k5, o_exp_k5, HP_K5, (M ** 5) / (N_EXP ** 2), k6, o_exp_k6, HP_K6,
                   (M ** 6) / (N_EXP ** 2), R_EXPAND, k5, o_van_k5, detail["sparsify_crater_confirmed"], traj),
                detail)
    return ("HARD_FAIL",
            "HARD_FAIL: expansion did NOT rescue K%d (oracle_any=%.3f < %.2f) despite the disentangler "
            "proving expansion lowers ORACLE crosstalk_std ~1.96x -- crosstalk fell but BASIN reachability "
            "did not recover, sharpening the basin-count-vs-crosstalk distinction (informative negative). "
            "Vanilla K%d=%.3f. %s"
            % (k5, o_exp_k5, HP_K5, k5, o_van_k5, traj), detail)


def main() -> None:
    output_dir = get_output_dir(ANCHOR_NAME)
    total = EXPECTED_N_UNITS
    _write_start_marker(output_dir, total)
    print("[config] anchor=%s mode=%s N_base=%d N_exp=%d(r=%d) M=%d MAXIT=%d R=%d TR=%d T0=%s K=%s "
          "arms=%s seeds=%s dev=%s expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, N_BASE, N_EXP, R_EXPAND, M, MAXIT, R, TR, T0_GRID, K_GRID,
             ARMS, SEEDS, DEV, total), flush=True)
    t0 = time.perf_counter()
    run_config = {"N_BASE": N_BASE, "N_EXP": N_EXP, "M": M, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, output_dir, run_config=run_config)
    print("[ckpt] %d/%d seeds done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        res = run_seed(seed, output_dir, t0,
                       unit_base=(len(done) + i) * len(K_GRID) * len(ARMS), total=total)
        write_partial(output_dir, seed, res)

    per_seed = list(aggregate_partials(output_dir, SEEDS, run_config=run_config).values())
    if len(per_seed) != len(SEEDS):
        raise RuntimeError("HARD_FAIL_CARDINALITY_META_RULE_H: expected %d seeds got %d"
                           % (len(SEEDS), len(per_seed)))
    for ps in per_seed:
        n = sum(1 for _ in ps["by"])
        if n != len(K_GRID) * len(ARMS):
            raise RuntimeError("HARD_FAIL_CARDINALITY_META_RULE_H: seed %s has %d arms expected %d"
                               % (ps.get("seed"), n, len(K_GRID) * len(ARMS)))

    verdict, vmsg, detail = build_verdict(per_seed)

    # SMOKE discriminator-fires gate: expansion must lift over CRATERED vanilla at the crater-BOUNDARY-K.
    # The wall location scales with N (crater-K = smallest K with M^K/N_exp^2 > ~1), so we scan for ANY K
    # where vanilla craters and expansion lifts -- NOT the full's calibrated 0.70 band (unreachable at
    # smoke N). This is the discriminator-survives-scale evidence; the FULL judges the shifted K5/K6.
    boundary_k = None
    best_lift = -1.0
    for K in K_GRID:
        ov = detail["oracle_any"]["vanilla"][str(K)]
        oe = detail["oracle_any"]["expansion"][str(K)]
        if ov < VANILLA_CRATER_CEIL and (oe - ov) > best_lift:
            best_lift = oe - ov
            boundary_k = K
    detail["smoke_boundary_k"] = boundary_k
    detail["smoke_expansion_lift"] = best_lift
    detail["smoke_discriminator_fired"] = bool(boundary_k is not None and best_lift >= 0.20)
    if SMOKE:
        if detail["smoke_discriminator_fired"]:
            print("[SMOKE_GATE_PASS] expansion rescues crater-boundary K%d: lift=%.3f over cratered "
                  "vanilla. Expansion lever moves reachability at scale; FULL judges shifted K5/K6."
                  % (boundary_k, best_lift), flush=True)
        else:
            print("[SMOKE_GATE_FAIL] no K where vanilla craters (<%.2f) AND expansion lifts >=0.20. "
                  "Expansion lever did not move reachability; DO NOT dispatch FULL." % VANILLA_CRATER_CEIL,
                  flush=True)

    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
               "run_mode": RUN_MODE, "n_seeds": len(per_seed), "per_seed": per_seed, "detail": detail,
               "config": {"N_BASE": N_BASE, "N_EXP": N_EXP, "R_EXPAND": R_EXPAND, "M": M, "MAXIT": MAXIT,
                          "R": R, "TR": TR, "T0_GRID": T0_GRID, "K_GRID": K_GRID, "ARMS": ARMS,
                          "SEEDS": SEEDS, "SPARSITY": SPARSITY, "EXPECTED_N_UNITS": EXPECTED_N_UNITS},
               "elapsed_s": time.perf_counter() - t0}
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
