"""meta_knowledge_tip_of_tongue_v2_ratio_smoke -- TOT criterion redesign.

Tests v1 TEST_DESIGN_FAILURE remediation per drill 2026-06-27. Same codebook
construction (clustered, OFFSET_AMPLITUDE=0.5) and same SNR sweep as v1; the
only change is the TOT discriminator. Three discriminators evaluated on the
SAME query stream (zero extra compute):

  Discr_v1 (legacy):   cleanup_margin < Q30(clean) AND cluster_cos > Q50(clean)
  Discr_C  (ratio):    cluster_cos / max(cleanup_top1, 0.05) > 2.0 AND cluster_cos > 0.30
  Discr_B  (absolute): cluster_cos in [0.30, 0.55] AND cleanup_top1 < 0.20

TOP-1 redesign = Discr_C (ratio). Brain-grounded per Brown-McNeill 1966 +
Yonelinas dual-process + Schwartz cue-familiarity (decoupled channels).

PRE-REG HARD_PASS (conjunctive):
  Discr_C peak SNR interior (in {0.3, 0.5, 0.7}) AND
  Discr_C peak TOT-rate >= 0.30 AND
  cluster_acc_in_TOT @ peak >= 0.65 AND
  HC_atom_recall >= 0.80 AND
  LC_refuse_rate >= 0.90 AND
  Discr_v1 vs Discr_C peak agreement within +/-1 sweep step

HARD_FAIL (any one):
  Discr_C peak at endpoint (SNR=0.2 or 1.0)
  Discr_C peak TOT-rate < 0.10
  cluster_acc_in_TOT @ peak < 0.50
  HC_atom_recall < 0.70
  Discr_C and Discr_v1 peak-SNR disagree by >= 2 sweep steps

MIDDLE_BAND:
  Discr_C peak-TOT-rate in [0.10, 0.30] OR cluster_acc_in_TOT in [0.50, 0.65]

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 4 arms * 3 seeds * 5000 queries = 60000
  EXPECTED_N_UNITS_SMOKE = 4 arms * 2 seeds * 300  queries = 2400

HARDENING (META_RULE_X / L1-L4):
  main wrapped in if __name__ == "__main__"
  L1: minimal metrics.json with STARTED + PID at start
  L2: per-arm progress updates
  L3: outer try/except around main; SystemExit re-raised FIRST
  L4: import-crash sentinel

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (Opus 4.7 1M).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "meta_knowledge_tip_of_tongue_v2_ratio"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init.
# Discr_C (ratio, TOP-1) thresholds — brain-grounded per drill 2026-06-27.
HP_PEAK_INTERIOR_SET = {0.3, 0.5, 0.7}
HP_DISCR_C_PEAK_TOT_MIN = 0.30
HP_CLUSTER_ACC_AT_PEAK_MIN = 0.65
HP_HIGH_CONF_RECALL_MIN = 0.80
HP_LOW_CONF_REFUSE_MIN = 0.90
HP_V1_VS_C_SWEEP_STEP_TOL = 1

HF_DISCR_C_PEAK_TOT_LO = 0.10
HF_CLUSTER_ACC_AT_PEAK_LO = 0.50
HF_HIGH_CONF_RECALL_LO = 0.70
HF_V1_VS_C_DISAGREE_STEPS = 2

MB_DISCR_C_PEAK_TOT_LO = 0.10
MB_DISCR_C_PEAK_TOT_HI = 0.30
MB_CLUSTER_ACC_AT_PEAK_LO = 0.50
MB_CLUSTER_ACC_AT_PEAK_HI = 0.65

# Discr_v1 (legacy, calibrated against SNR=1.0 clean dist)
TOT_CLEANUP_QUANTILE = 0.30
TOT_CLUSTER_QUANTILE = 0.50

# Discr_C (ratio) constants
DISCR_C_RATIO_THR = 2.0
DISCR_C_RATIO_DENOM_FLOOR = 0.05
DISCR_C_CLUSTER_FLOOR = 0.30

# Discr_B (absolute) bands
DISCR_B_CLUSTER_LO = 0.30
DISCR_B_CLUSTER_HI = 0.55
DISCR_B_CLEANUP_TOP1_HI = 0.20

EXPECTED_ARMS = [
    "high_conf_high_recall", "tot_partial_know",
    "low_conf_low_recall", "diag_tot_rate_vs_snr",
]

if SELF_TEST_MODE:
    N_DIM = 256
    V_ATOMS = 200
    K_CLUSTERS = 10
    N_QUERIES_PER_ARM = 80
    SEEDS = [7]
    SNR_SWEEP = [0.2, 0.5, 0.8, 1.0]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V_ATOMS = 500
    K_CLUSTERS = 10
    N_QUERIES_PER_ARM = 300
    SEEDS = [7, 17]
    SNR_SWEEP = [0.2, 0.3, 0.5, 0.7, 1.0]
else:
    N_DIM = 2048
    V_ATOMS = 2000
    K_CLUSTERS = 10
    N_QUERIES_PER_ARM = 5000
    SEEDS = [7, 17, 23]
    SNR_SWEEP = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_QUERIES_PER_ARM

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,K=%d,Q=%d,SNR=%s,seeds=%s,mode=%s,"
    "DISCR_C_RATIO_THR=%.2f,DISCR_C_CLU_FLOOR=%.2f,"
    "DISCR_B_CLU=[%.2f,%.2f],DISCR_B_TOP1<=%.2f,"
    "HP_peak_TOT_C>=%.2f,HP_peak_clusterAcc>=%.2f,"
    "expected_n=%d,hardening=L1early+L2perarm+L3outertry+L4importsentinel+SysExitFirst"
) % (
    ANCHOR_NAME, N_DIM, V_ATOMS, K_CLUSTERS, N_QUERIES_PER_ARM, SNR_SWEEP,
    SEEDS, RUN_MODE,
    DISCR_C_RATIO_THR, DISCR_C_CLUSTER_FLOOR,
    DISCR_B_CLUSTER_LO, DISCR_B_CLUSTER_HI, DISCR_B_CLEANUP_TOP1_HI,
    HP_DISCR_C_PEAK_TOT_MIN, HP_CLUSTER_ACC_AT_PEAK_MIN, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v2_ratio_meta_knowledge_tip_of_tongue",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v2_ratio_meta_knowledge_tip_of_tongue_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ----------------------- primitives (inherited from v1) -----------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def make_clustered_codebook(V: int, K: int, n: int, g: np.random.Generator):
    centroids = bipolar(K, n, g)
    cluster_ids = g.integers(0, K, size=V)
    atoms = np.zeros((V, n), dtype=np.float32)
    OFFSET_AMPLITUDE = 0.5
    for i in range(V):
        c = centroids[cluster_ids[i]]
        offset_bipolar = (g.integers(0, 2, size=n) * 2 - 1).astype(np.float32)
        v = c + OFFSET_AMPLITUDE * offset_bipolar
        atoms[i] = v / (np.linalg.norm(v) + 1e-8)
    return atoms, centroids, cluster_ids


def make_noisy_query_v2(atom: np.ndarray, snr: float,
                          g: np.random.Generator,
                          atoms: np.ndarray = None,
                          cluster_id: int = None,
                          cluster_ids: np.ndarray = None) -> np.ndarray:
    n = atom.shape[0]
    s = max(0.0, min(1.0, snr))
    if atoms is None or cluster_id is None or cluster_ids is None:
        noise = g.standard_normal(n).astype(np.float32)
        noise = noise / (np.linalg.norm(noise) + 1e-8)
        q = s * atom + (1.0 - s) * noise
        return q / (np.linalg.norm(q) + 1e-8)
    sibling_mask = (cluster_ids == cluster_id)
    sibling_idx_all = np.where(sibling_mask)[0]
    if len(sibling_idx_all) <= 1:
        noise = g.standard_normal(n).astype(np.float32)
        noise = noise / (np.linalg.norm(noise) + 1e-8)
    else:
        n_sample = min(5, len(sibling_idx_all))
        chosen = g.choice(sibling_idx_all, size=n_sample, replace=False)
        sib = atoms[chosen].mean(axis=0)
        gn = g.standard_normal(n).astype(np.float32) * 0.1
        noise = (sib + gn) / (np.linalg.norm(sib + gn) + 1e-8)
    q = s * atom + (1.0 - s) * noise
    return q / (np.linalg.norm(q) + 1e-8)


def _query_signals(idx: int, q: np.ndarray, atoms: np.ndarray,
                    centroids: np.ndarray, cluster_ids: np.ndarray):
    sims = atoms @ q
    top_idx = int(np.argmax(sims))
    top_sim = float(sims[top_idx])
    sorted_sims = np.sort(sims)[::-1]
    cleanup_margin = float(sorted_sims[0] - sorted_sims[1]) if len(sorted_sims) > 1 else float(sorted_sims[0])
    cluster_sims = centroids @ q
    top_clu = int(np.argmax(cluster_sims))
    top_clu_sim = float(cluster_sims[top_clu])
    atom_correct = (top_idx == idx)
    cluster_correct = (top_clu == cluster_ids[idx])
    return (top_idx, top_sim, cleanup_margin, top_clu, top_clu_sim,
            atom_correct, cluster_correct)


# ----------------------- discriminators -----------------------

def discr_v1_fires(cleanup_margin: float, cluster_cos: float,
                    cleanup_thr: float, cluster_thr: float) -> bool:
    """Legacy: percentile-relative cleanup_margin + cluster_cos."""
    return (cleanup_margin < cleanup_thr) and (cluster_cos > cluster_thr)


def discr_C_fires(cleanup_top1: float, cluster_cos: float) -> bool:
    """Ratio criterion (TOP-1): cluster/cleanup ratio + cluster floor."""
    ratio = cluster_cos / max(cleanup_top1, DISCR_C_RATIO_DENOM_FLOOR)
    return (ratio > DISCR_C_RATIO_THR) and (cluster_cos > DISCR_C_CLUSTER_FLOOR)


def discr_B_fires(cleanup_top1: float, cluster_cos: float) -> bool:
    """Absolute bands."""
    return ((DISCR_B_CLUSTER_LO <= cluster_cos <= DISCR_B_CLUSTER_HI)
            and (cleanup_top1 < DISCR_B_CLEANUP_TOP1_HI))


# ----------------------- per-seed runner -----------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    atoms, centroids, cluster_ids = make_clustered_codebook(
        V_ATOMS, K_CLUSTERS, N_DIM, g)

    per_arm: Dict[str, Dict[str, Any]] = {}
    n_q = N_QUERIES_PER_ARM

    # -------------- PASS A: HIGH_CONF (SNR=1.0) -- CALIBRATE Discr_v1 thresholds --------------
    hc_cleanup_margins: List[float] = []
    hc_cluster_sims: List[float] = []
    hc_atom_correct = 0
    hc_cluster_correct = 0
    for _ in range(n_q):
        idx = int(g.integers(0, V_ATOMS))
        q = make_noisy_query_v2(atoms[idx], snr=1.0, g=g, atoms=atoms,
                                 cluster_id=int(cluster_ids[idx]),
                                 cluster_ids=cluster_ids)
        _, ts, cm, _, tcs, ac, cc = _query_signals(idx, q, atoms, centroids, cluster_ids)
        hc_cleanup_margins.append(cm)
        hc_cluster_sims.append(tcs)
        if ac:
            hc_atom_correct += 1
        if cc:
            hc_cluster_correct += 1
    hc_cleanup_arr = np.array(hc_cleanup_margins)
    hc_cluster_arr = np.array(hc_cluster_sims)
    cleanup_thr = float(np.quantile(hc_cleanup_arr, TOT_CLEANUP_QUANTILE))
    cluster_thr = float(np.quantile(hc_cluster_arr, TOT_CLUSTER_QUANTILE))

    # -------------- PASS C: OOD (random) -- refuse threshold --------------
    ood_cleanup_sims: List[float] = []
    for _ in range(n_q):
        q = g.standard_normal(N_DIM).astype(np.float32)
        q = q / (np.linalg.norm(q) + 1e-8)
        sims = atoms @ q
        ood_cleanup_sims.append(float(sims.max()))
    ood_arr = np.array(ood_cleanup_sims)
    ood_mean = float(ood_arr.mean())
    ood_std = float(ood_arr.std() + 1e-8)
    refuse_thr = ood_mean + 3.0 * ood_std

    hc_top1_sims = []
    for _ in range(n_q):
        idx = int(g.integers(0, V_ATOMS))
        q = make_noisy_query_v2(atoms[idx], snr=1.0, g=g, atoms=atoms,
                                 cluster_id=int(cluster_ids[idx]),
                                 cluster_ids=cluster_ids)
        sims = atoms @ q
        hc_top1_sims.append(float(sims.max()))
    hc_top1_arr = np.array(hc_top1_sims)
    hc_refuse = int(np.sum(hc_top1_arr < refuse_thr))
    per_arm["high_conf_high_recall"] = {
        "atom_recall": hc_atom_correct / n_q,
        "cluster_recall": hc_cluster_correct / n_q,
        "refuse_rate": hc_refuse / n_q,
        "cleanup_thr_calibrated": cleanup_thr,
        "cluster_thr_calibrated": cluster_thr,
        "refuse_thr": refuse_thr,
        "n": n_q,
    }

    ood_refuse = int(np.sum(ood_arr < refuse_thr))
    per_arm["low_conf_low_recall"] = {
        "refuse_rate": ood_refuse / n_q,
        "mean_top1_sim": ood_mean,
        "ood_std": ood_std,
        "refuse_thr": refuse_thr,
        "n": n_q,
    }

    # -------------- PASS B: TOT (SNR=0.3, 0.6 mix) -- three discriminators --------------
    tot_correct = 0
    tot_cluster_correct = 0
    snr_choices = [0.3, 0.6]
    cnt_v1 = 0; cca_v1 = 0
    cnt_C = 0; cca_C = 0
    cnt_B = 0; cca_B = 0
    for _ in range(n_q):
        idx = int(g.integers(0, V_ATOMS))
        snr = snr_choices[int(g.integers(0, 2))]
        q = make_noisy_query_v2(atoms[idx], snr=snr, g=g, atoms=atoms,
                                 cluster_id=int(cluster_ids[idx]),
                                 cluster_ids=cluster_ids)
        _, ts, cm, top_clu, tcs, ac, cc = _query_signals(idx, q, atoms, centroids, cluster_ids)
        if ac:
            tot_correct += 1
        if cc:
            tot_cluster_correct += 1
        if discr_v1_fires(cm, tcs, cleanup_thr, cluster_thr):
            cnt_v1 += 1
            if cc:
                cca_v1 += 1
        if discr_C_fires(ts, tcs):
            cnt_C += 1
            if cc:
                cca_C += 1
        if discr_B_fires(ts, tcs):
            cnt_B += 1
            if cc:
                cca_B += 1
    per_arm["tot_partial_know"] = {
        "atom_recall": tot_correct / n_q,
        "cluster_recall": tot_cluster_correct / n_q,
        "discr_v1_tot_rate": cnt_v1 / n_q,
        "discr_v1_cluster_acc_in_tot": (cca_v1 / cnt_v1) if cnt_v1 > 0 else 0.0,
        "discr_v1_count": cnt_v1,
        "discr_C_tot_rate": cnt_C / n_q,
        "discr_C_cluster_acc_in_tot": (cca_C / cnt_C) if cnt_C > 0 else 0.0,
        "discr_C_count": cnt_C,
        "discr_B_tot_rate": cnt_B / n_q,
        "discr_B_cluster_acc_in_tot": (cca_B / cnt_B) if cnt_B > 0 else 0.0,
        "discr_B_count": cnt_B,
        "n": n_q,
    }

    # -------------- ARM 4: DIAG_TOT_RATE_VS_SNR (sweep) -- three discriminators --------------
    diag_results: List[Dict[str, Any]] = []
    per_snr_q = max(40, n_q // len(SNR_SWEEP))
    for snr in SNR_SWEEP:
        a_correct = 0
        c_correct = 0
        cn_v1 = 0; ca_v1 = 0
        cn_C = 0; ca_C = 0
        cn_B = 0; ca_B = 0
        for _ in range(per_snr_q):
            idx = int(g.integers(0, V_ATOMS))
            q = make_noisy_query_v2(atoms[idx], snr=snr, g=g, atoms=atoms,
                                 cluster_id=int(cluster_ids[idx]),
                                 cluster_ids=cluster_ids)
            _, ts, cm, _, tcs, ac, cc = _query_signals(idx, q, atoms, centroids, cluster_ids)
            if ac:
                a_correct += 1
            if cc:
                c_correct += 1
            if discr_v1_fires(cm, tcs, cleanup_thr, cluster_thr):
                cn_v1 += 1
                if cc:
                    ca_v1 += 1
            if discr_C_fires(ts, tcs):
                cn_C += 1
                if cc:
                    ca_C += 1
            if discr_B_fires(ts, tcs):
                cn_B += 1
                if cc:
                    ca_B += 1
        diag_results.append({
            "snr": float(snr),
            "atom_recall": a_correct / per_snr_q,
            "cluster_recall": c_correct / per_snr_q,
            "discr_v1_tot_rate": cn_v1 / per_snr_q,
            "discr_v1_cluster_acc_in_tot": (ca_v1 / cn_v1) if cn_v1 > 0 else 0.0,
            "discr_C_tot_rate": cn_C / per_snr_q,
            "discr_C_cluster_acc_in_tot": (ca_C / cn_C) if cn_C > 0 else 0.0,
            "discr_B_tot_rate": cn_B / per_snr_q,
            "discr_B_cluster_acc_in_tot": (ca_B / cn_B) if cn_B > 0 else 0.0,
            "n": per_snr_q,
        })
    per_arm["diag_tot_rate_vs_snr"] = {
        "sweep": diag_results,
        "n_snr_levels": len(SNR_SWEEP),
        "cleanup_thr_used": cleanup_thr,
        "cluster_thr_used": cluster_thr,
    }

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm,
    }


# ----------------------- aggregate + verdict -----------------------

def _peak_pattern(per_snr_tot: Dict[float, float],
                   per_snr_cca: Dict[float, float],
                   snr_sorted: List[float]) -> Dict[str, Any]:
    if not per_snr_tot:
        return {"peak_snr": None, "peak_tot_rate": 0.0,
                "peak_cluster_acc": 0.0, "is_interior": False,
                "per_snr_tot_rate": {}, "per_snr_cluster_acc": {}}
    peak_snr = max(per_snr_tot, key=lambda s: per_snr_tot[s])
    is_interior = (peak_snr != snr_sorted[0] and peak_snr != snr_sorted[-1])
    return {
        "peak_snr": float(peak_snr),
        "peak_tot_rate": float(per_snr_tot[peak_snr]),
        "peak_cluster_acc": float(per_snr_cca[peak_snr]),
        "is_interior": bool(is_interior),
        "per_snr_tot_rate": {float(k): float(v) for k, v in per_snr_tot.items()},
        "per_snr_cluster_acc": {float(k): float(v) for k, v in per_snr_cca.items()},
    }


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_arm": {}}

    hc_atom_recalls: List[float] = []
    lc_refuse_rates: List[float] = []
    per_arm_full: Dict[str, Dict[str, Dict[str, Any]]] = {arm: {} for arm in EXPECTED_ARMS}
    for s_key, body in per_seed.items():
        pa = body.get("per_arm", {})
        for arm in EXPECTED_ARMS:
            if arm in pa:
                per_arm_full[arm][s_key] = pa[arm]
        if "high_conf_high_recall" in pa:
            hc_atom_recalls.append(pa["high_conf_high_recall"]["atom_recall"])
        if "low_conf_low_recall" in pa:
            lc_refuse_rates.append(pa["low_conf_low_recall"]["refuse_rate"])

    hc_recall_mean = float(np.mean(hc_atom_recalls)) if hc_atom_recalls else 0.0
    lc_refuse_mean = float(np.mean(lc_refuse_rates)) if lc_refuse_rates else 0.0

    # Aggregate diag sweep per-SNR across seeds for each discriminator
    per_snr_v1_tot: Dict[float, List[float]] = {}
    per_snr_v1_cca: Dict[float, List[float]] = {}
    per_snr_C_tot: Dict[float, List[float]] = {}
    per_snr_C_cca: Dict[float, List[float]] = {}
    per_snr_B_tot: Dict[float, List[float]] = {}
    per_snr_B_cca: Dict[float, List[float]] = {}
    for s_key, body in per_arm_full["diag_tot_rate_vs_snr"].items():
        for d in body.get("sweep", []):
            snr = float(d["snr"])
            per_snr_v1_tot.setdefault(snr, []).append(float(d.get("discr_v1_tot_rate", 0.0)))
            per_snr_v1_cca.setdefault(snr, []).append(float(d.get("discr_v1_cluster_acc_in_tot", 0.0)))
            per_snr_C_tot.setdefault(snr, []).append(float(d.get("discr_C_tot_rate", 0.0)))
            per_snr_C_cca.setdefault(snr, []).append(float(d.get("discr_C_cluster_acc_in_tot", 0.0)))
            per_snr_B_tot.setdefault(snr, []).append(float(d.get("discr_B_tot_rate", 0.0)))
            per_snr_B_cca.setdefault(snr, []).append(float(d.get("discr_B_cluster_acc_in_tot", 0.0)))
    snr_sorted = sorted(per_snr_C_tot.keys()) if per_snr_C_tot else []
    mean_v1_tot = {s: float(np.mean(per_snr_v1_tot[s])) for s in snr_sorted}
    mean_v1_cca = {s: float(np.mean(per_snr_v1_cca[s])) for s in snr_sorted}
    mean_C_tot = {s: float(np.mean(per_snr_C_tot[s])) for s in snr_sorted}
    mean_C_cca = {s: float(np.mean(per_snr_C_cca[s])) for s in snr_sorted}
    mean_B_tot = {s: float(np.mean(per_snr_B_tot[s])) for s in snr_sorted}
    mean_B_cca = {s: float(np.mean(per_snr_B_cca[s])) for s in snr_sorted}

    peak_v1 = _peak_pattern(mean_v1_tot, mean_v1_cca, snr_sorted)
    peak_C = _peak_pattern(mean_C_tot, mean_C_cca, snr_sorted)
    peak_B = _peak_pattern(mean_B_tot, mean_B_cca, snr_sorted)

    # Sweep-step agreement between Discr_v1 and Discr_C
    v1_vs_C_step_delta = None
    if peak_v1["peak_snr"] is not None and peak_C["peak_snr"] is not None and snr_sorted:
        try:
            i_v1 = snr_sorted.index(peak_v1["peak_snr"])
            i_C = snr_sorted.index(peak_C["peak_snr"])
            v1_vs_C_step_delta = abs(i_v1 - i_C)
        except ValueError:
            v1_vs_C_step_delta = None

    # Verdict (Discr_C is TOP-1)
    verdict = "MIDDLE_BAND"
    hard_fail_reasons: List[str] = []
    hard_pass_reasons: List[str] = []

    pc = peak_C
    # HARD_FAIL checks
    if pc["peak_snr"] is None:
        hard_fail_reasons.append("Discr_C has no peak (no sweep data)")
    else:
        if not pc["is_interior"]:
            hard_fail_reasons.append("Discr_C peak at endpoint SNR=%.2f" % pc["peak_snr"])
        if pc["peak_tot_rate"] < HF_DISCR_C_PEAK_TOT_LO:
            hard_fail_reasons.append("Discr_C peak TOT-rate %.3f < %.2f" % (pc["peak_tot_rate"], HF_DISCR_C_PEAK_TOT_LO))
        if pc["peak_cluster_acc"] < HF_CLUSTER_ACC_AT_PEAK_LO:
            hard_fail_reasons.append("cluster_acc_in_TOT@peak %.3f < %.2f" % (pc["peak_cluster_acc"], HF_CLUSTER_ACC_AT_PEAK_LO))
    if hc_recall_mean < HF_HIGH_CONF_RECALL_LO:
        hard_fail_reasons.append("HC_recall %.3f < %.2f" % (hc_recall_mean, HF_HIGH_CONF_RECALL_LO))
    if v1_vs_C_step_delta is not None and v1_vs_C_step_delta >= HF_V1_VS_C_DISAGREE_STEPS:
        hard_fail_reasons.append("Discr_v1 vs Discr_C peak-SNR disagree by %d steps" % v1_vs_C_step_delta)

    # HARD_PASS checks (only if no HARD_FAIL triggers)
    if not hard_fail_reasons and pc["peak_snr"] is not None:
        cond_interior = pc["peak_snr"] in HP_PEAK_INTERIOR_SET
        cond_tot = pc["peak_tot_rate"] >= HP_DISCR_C_PEAK_TOT_MIN
        cond_cca = pc["peak_cluster_acc"] >= HP_CLUSTER_ACC_AT_PEAK_MIN
        cond_hc = hc_recall_mean >= HP_HIGH_CONF_RECALL_MIN
        cond_lc = lc_refuse_mean >= HP_LOW_CONF_REFUSE_MIN
        cond_agree = (v1_vs_C_step_delta is not None and
                      v1_vs_C_step_delta <= HP_V1_VS_C_SWEEP_STEP_TOL)
        all_pass = cond_interior and cond_tot and cond_cca and cond_hc and cond_lc and cond_agree
        hard_pass_reasons = [
            "interior=%s" % cond_interior,
            "C_peak_TOT(%.3f>=%.2f)=%s" % (pc["peak_tot_rate"], HP_DISCR_C_PEAK_TOT_MIN, cond_tot),
            "cca(%.3f>=%.2f)=%s" % (pc["peak_cluster_acc"], HP_CLUSTER_ACC_AT_PEAK_MIN, cond_cca),
            "HC(%.3f>=%.2f)=%s" % (hc_recall_mean, HP_HIGH_CONF_RECALL_MIN, cond_hc),
            "LC(%.3f>=%.2f)=%s" % (lc_refuse_mean, HP_LOW_CONF_REFUSE_MIN, cond_lc),
            "agree(delta=%s<=%d)=%s" % (str(v1_vs_C_step_delta), HP_V1_VS_C_SWEEP_STEP_TOL, cond_agree),
        ]
        if all_pass:
            verdict = "HARD_PASS"

    if hard_fail_reasons:
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | Discr_C peak_SNR=%s peak_TOT=%.3f peak_cca=%.3f interior=%s | "
        "Discr_v1 peak_SNR=%s peak_TOT=%.3f | step_delta=%s | "
        "HC=%.3f LC=%.3f | reasons=%s"
    ) % (verdict,
         str(pc["peak_snr"]), pc["peak_tot_rate"], pc["peak_cluster_acc"], pc["is_interior"],
         str(peak_v1["peak_snr"]), peak_v1["peak_tot_rate"], str(v1_vs_C_step_delta),
         hc_recall_mean, lc_refuse_mean,
         "|".join(hard_fail_reasons) if hard_fail_reasons else (";".join(hard_pass_reasons) if hard_pass_reasons else "MB"))

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "peak_discr_v1": peak_v1,
        "peak_discr_C": peak_C,
        "peak_discr_B": peak_B,
        "v1_vs_C_sweep_step_delta": v1_vs_C_step_delta,
        "high_conf_atom_recall_mean": hc_recall_mean,
        "low_conf_refuse_rate_mean": lc_refuse_mean,
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(EXPECTED_ARMS) * N_QUERIES_PER_ARM,
        "cardinality_ok": (len(per_seed) >= 2),
        "hard_fail_reasons": hard_fail_reasons,
        "hard_pass_reasons": hard_pass_reasons,
    }


# ----------------------- main -----------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS})

    print("[%s] mode=%s N=%d V=%d K=%d Q=%d SNR=%s seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_ATOMS, K_CLUSTERS, N_QUERIES_PER_ARM,
        SNR_SWEEP, SEEDS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
            tot = r["per_arm"]["tot_partial_know"]
            assert "discr_C_tot_rate" in tot, "missing discr_C_tot_rate"
            assert "discr_v1_tot_rate" in tot, "missing discr_v1_tot_rate"
            assert "discr_B_tot_rate" in tot, "missing discr_B_tot_rate"
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: 3-discriminator structure verified",
                                   extra={"_phase": "selftest_done",
                                          "selftest_arms": list(r["per_arm"].keys()),
                                          "selftest_discr_C_tot": tot["discr_C_tot_rate"],
                                          "selftest_discr_v1_tot": tot["discr_v1_tot_rate"]})
            print("[selftest] OK; discr_C_tot=%.3f discr_v1_tot=%.3f" % (
                tot["discr_C_tot_rate"], tot["discr_v1_tot_rate"]), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_ratio_meta_knowledge_tip_of_tongue"
    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
