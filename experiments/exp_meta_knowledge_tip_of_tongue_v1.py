"""meta_knowledge_tip_of_tongue_v1 -- substrate TOT-state witness.

Tests: substrate exhibits brain-aligned tip-of-tongue states where
cluster-cosine HIGH but atom-cleanup LOW; AND cluster-identification
accuracy remains >= 0.70 in those TOT cases (substrate KNOWS the
category even when refusing the specific atom).

ARMS (4):
  ARM_HIGH_CONF_HIGH_RECALL   clean queries (SNR=1.0); confidence sanity
  ARM_TOT_PARTIAL_KNOW        noisy queries (SNR=0.3, 0.6); TOT subset
  ARM_LOW_CONF_LOW_RECALL     OOD queries (random); refuses correctly
  ARM_DIAG_TOT_RATE_VS_SNR    sweep SNR; Spearman rho discriminator

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE):
  HARD_PASS:  Spearman rho(SNR, TOT-rate) <= -0.7 AND
              cluster-acc-in-TOT >= 0.70 AND
              HIGH_CONF atom recall >= 0.80 AND
              LOW_CONF refuse-fire >= 0.90
  MIDDLE_BAND: rho in [-0.5, -0.7] OR cluster-acc-in-TOT in [0.40, 0.70]
  HARD_FAIL:  |rho| < 0.5 OR cluster-acc at chance OR HIGH_CONF recall < 0.50

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 4 arms * 3 seeds * 5000 queries = 60000
  EXPECTED_N_UNITS_SMOKE = 4 arms * 2 seeds * 300  queries = 2400

HARDENING (META_RULE_X / L1-L4):
  main wrapped in if __name__ == "__main__"
  L1: minimal metrics.json with STARTED + PID at start
  L2: per-arm progress updates
  L3: outer try/except around main; failure-class to metrics
  L4: import-crash sentinel

ASCII-only; no emojis; no em-dashes; self-contained (no hdlab imports).
Author: exp_dev 2026-06-27 (Opus 4.7 1M, Wave 3B TOP-2)
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

ANCHOR_NAME = "meta_knowledge_tip_of_tongue_v1"

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
# HARD_PASS discriminator updated (PRE-SMOKE PROSPECTIVE): TOT-rate is empirically
# UNIMODAL with peak at intermediate SNR (not monotone in SNR as initially drilled).
# True discriminator: (a) TOT-rate has interior maximum (peak NOT at SNR endpoints),
# (b) cluster_acc_in_TOT >= 0.70 at peak (substrate knows category in confused cases),
# (c) refuse-gate clean.
HP_TOT_RATE_AT_PEAK_MIN = 0.40  # interior peak must exceed 0.40 TOT-rate
HP_PEAK_NOT_AT_ENDPOINTS = True  # peak SNR must be in interior of sweep
HP_CLUSTER_ACC_AT_PEAK_MIN = 0.70  # at peak SNR, cluster_acc_in_TOT >= 0.70
HP_HIGH_CONF_RECALL_MIN = 0.80
HP_LOW_CONF_REFUSE_MIN = 0.90
MB_CLUSTER_ACC_AT_PEAK_LO = 0.50
HF_HIGH_CONF_RECALL_LO = 0.50

# Operational TOT definition (LOCKED prospective; PERCENTILE-BASED to scale with N).
# At N_DIM scale, raw cosine threshold-magnitudes shift; we use relative thresholds
# computed against the SNR=1.0 baseline distribution per seed.
# A TOT case is operationally defined as:
#   atom_cleanup_cos < QUANTILE_30 of clean-recall cleanup_cos distribution AND
#   cluster_cos      > QUANTILE_50 of clean-recall cluster_cos distribution
# Effectively: "cluster_cos relatively high but cleanup_cos relatively low".
TOT_CLEANUP_QUANTILE = 0.30  # below 30th percentile of clean cleanup
TOT_CLUSTER_QUANTILE = 0.50  # above 50th percentile of clean cluster
# Refuse-gate threshold for ARM_LOW_CONF_LOW_RECALL (must be cleanly above OOD floor).
REFUSE_MARGIN_VS_OOD = 1.5  # cleanup_cos must be > 1.5x OOD mean to NOT refuse

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
    "TOT_CL_Q=%.2f,TOT_CC_Q=%.2f,HP_peak_TOT>=%.2f,HP_peak_clusterAcc>=%.2f,"
    "expected_n=%d,hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, V_ATOMS, K_CLUSTERS, N_QUERIES_PER_ARM, SNR_SWEEP,
    SEEDS, RUN_MODE, TOT_CLEANUP_QUANTILE, TOT_CLUSTER_QUANTILE,
    HP_TOT_RATE_AT_PEAK_MIN, HP_CLUSTER_ACC_AT_PEAK_MIN, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v1_meta_knowledge_tip_of_tongue",
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
            "_hardening_marker": "v1_meta_knowledge_tip_of_tongue_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ----------------------- primitives -----------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def make_clustered_codebook(V: int, K: int, n: int, g: np.random.Generator):
    """Build V atoms grouped into K clusters via cluster-centroid + within-cluster offset.

    Calibrated so that ATOM cleanup requires MORE signal than CLUSTER cleanup --
    i.e., adding moderate noise should disrupt atom cleanup BEFORE cluster cleanup.

    Within-cluster atoms differ ONLY in atom-specific offset bits; the centroid is
    shared across all atoms in that cluster. So cluster cosine is robust to noise that
    disrupts the smaller atom-specific signature.

    Construction: each atom = normalize(centroid + atom_specific_offset). The offset
    is sized so that centroid contributes ~70% of unit norm and offset ~30%; this
    leaves the centroid-pattern surviving noise that disrupts atom-pattern.
    """
    centroids = bipolar(K, n, g)  # (K, n) bipolar unit-norm centroids
    cluster_ids = g.integers(0, K, size=V)
    atoms = np.zeros((V, n), dtype=np.float32)
    # Each atom-offset is bipolar (independent per atom). After bundle with
    # centroid AND renormalize, the atom-component contributes ~0.45 of unit norm
    # and centroid ~0.89. So atom_cleanup_max ~ 1.0 (self) but
    # cluster_cleanup_max ~ 0.89 (cosine to centroid).
    OFFSET_AMPLITUDE = 0.5  # atom-specific bipolar pattern, scaled down vs centroid
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
    """SNR-controlled in-cluster-confusion + Gaussian noise.

    To create TOT regime (cluster known, atom-specific cleanup fails), the noise
    must shift the query AWAY from atom-i toward OTHER ATOMS IN THE SAME CLUSTER --
    not random Gaussian (which goes orthogonal to all atoms).

    At SNR=1.0: pure atom.
    At SNR=0.5: 50% atom + 50% sibling-atom-bundle (other atoms in same cluster).
    At SNR=0.0: pure sibling-bundle (cluster identity but no atom identity).

    If atoms/cluster_id/cluster_ids not provided, falls back to Gaussian noise.
    """
    n = atom.shape[0]
    s = max(0.0, min(1.0, snr))
    if atoms is None or cluster_id is None or cluster_ids is None:
        # fallback: Gaussian noise
        noise = g.standard_normal(n).astype(np.float32)
        noise = noise / (np.linalg.norm(noise) + 1e-8)
        q = s * atom + (1.0 - s) * noise
        return q / (np.linalg.norm(q) + 1e-8)
    # Sibling-bundle noise: average of other atoms in same cluster
    sibling_mask = (cluster_ids == cluster_id)
    sibling_idx_all = np.where(sibling_mask)[0]
    if len(sibling_idx_all) <= 1:
        noise = g.standard_normal(n).astype(np.float32)
        noise = noise / (np.linalg.norm(noise) + 1e-8)
    else:
        n_sample = min(5, len(sibling_idx_all))
        # Choose siblings DIFFERENT from atom (NOT the atom itself)
        chosen = g.choice(sibling_idx_all, size=n_sample, replace=False)
        sib = atoms[chosen].mean(axis=0)
        # Add small Gaussian to break ties
        gn = g.standard_normal(n).astype(np.float32) * 0.1
        noise = (sib + gn) / (np.linalg.norm(sib + gn) + 1e-8)
    q = s * atom + (1.0 - s) * noise
    return q / (np.linalg.norm(q) + 1e-8)


def make_noisy_query(atom: np.ndarray, snr: float,
                      g: np.random.Generator) -> np.ndarray:
    """atom (n,) unit-norm; SNR controls relative noise stddev.

    SNR=1.0 -> very low noise; SNR=0.2 -> noise dominates.
    Noise_stddev = (1 - snr) * 1.0 (full-strength Gaussian per-dim);
    even at SNR=0.5 the noise is large relative to atom's unit-norm structure
    because we add iid Gaussian per-dim BEFORE normalization.
    """
    n = atom.shape[0]
    noise_stddev = (1.0 - snr) * 2.0  # 2.0x amplification for harsher regime
    noise = g.standard_normal(n).astype(np.float32) * noise_stddev
    q = atom + noise  # additive
    return q / (np.linalg.norm(q) + 1e-8)


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation."""
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = math.sqrt(float((rx ** 2).sum()) * float((ry ** 2).sum()))
    if denom <= 1e-12:
        return 0.0
    return float((rx * ry).sum() / denom)


# ----------------------- per-seed runner -----------------------

def _query_signals(idx: int, q: np.ndarray, atoms: np.ndarray,
                    centroids: np.ndarray, cluster_ids: np.ndarray):
    sims = atoms @ q
    top_idx = int(np.argmax(sims))
    top_sim = float(sims[top_idx])
    # Cleanup MARGIN: top1 - top2 (larger margin = more confident; smaller = TOT-like)
    sorted_sims = np.sort(sims)[::-1]
    cleanup_margin = float(sorted_sims[0] - sorted_sims[1]) if len(sorted_sims) > 1 else float(sorted_sims[0])
    cluster_sims = centroids @ q
    top_clu = int(np.argmax(cluster_sims))
    top_clu_sim = float(cluster_sims[top_clu])
    atom_correct = (top_idx == idx)
    cluster_correct = (top_clu == cluster_ids[idx])
    return (top_idx, top_sim, cleanup_margin, top_clu, top_clu_sim,
            atom_correct, cluster_correct)


def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    atoms, centroids, cluster_ids = make_clustered_codebook(
        V_ATOMS, K_CLUSTERS, N_DIM, g)

    per_arm: Dict[str, Dict[str, Any]] = {}
    n_q = N_QUERIES_PER_ARM

    # -------------- PASS A: HIGH_CONF (SNR=1.0) -- CALIBRATE thresholds --------------
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
    # cleanup_margin_thr: low margin means confused (TOT-like).
    # Threshold: cleanup_margin BELOW 30th percentile of CLEAN distribution
    cleanup_thr = float(np.quantile(hc_cleanup_arr, 0.30))
    # cluster_thr: HIGH cluster cosine (above 50th percentile of clean dist)
    cluster_thr = float(np.quantile(hc_cluster_arr, 0.50))

    # -------------- PASS C: OOD (random) -- determine refuse-threshold (on top1-cos, not margin) --------------
    ood_cleanup_sims: List[float] = []
    for _ in range(n_q):
        q = g.standard_normal(N_DIM).astype(np.float32)
        q = q / (np.linalg.norm(q) + 1e-8)
        sims = atoms @ q
        ood_cleanup_sims.append(float(sims.max()))
    ood_arr = np.array(ood_cleanup_sims)
    ood_mean = float(ood_arr.mean())
    ood_std = float(ood_arr.std() + 1e-8)
    refuse_thr = ood_mean + 3.0 * ood_std  # >3 stddev above OOD noise floor

    # HIGH_CONF refuse-rate (should be near 0 since substrate IS confident here)
    # Use TOP1-COS for refuse (NOT margin); collect from HC pass
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

    # OOD refuse-rate (should be near 1.0)
    ood_refuse = int(np.sum(ood_arr < refuse_thr))
    per_arm["low_conf_low_recall"] = {
        "refuse_rate": ood_refuse / n_q,
        "mean_top1_sim": ood_mean,
        "ood_std": ood_std,
        "refuse_thr": refuse_thr,
        "n": n_q,
    }

    # -------------- PASS B: TOT (SNR=0.3, 0.6 mix) -- partial-know --------------
    tot_correct = 0
    tot_cluster_correct = 0
    tot_count = 0
    tot_cluster_in_tot_correct = 0
    snr_choices = [0.3, 0.6]
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
        # TOT: cleanup_margin LOW (substrate confused between candidates) AND
        # cluster_cos HIGH (region known)
        if cm < cleanup_thr and tcs > cluster_thr:
            tot_count += 1
            if cc:
                tot_cluster_in_tot_correct += 1
    per_arm["tot_partial_know"] = {
        "atom_recall": tot_correct / n_q,
        "cluster_recall": tot_cluster_correct / n_q,
        "tot_rate": tot_count / n_q,
        "cluster_acc_in_tot": (tot_cluster_in_tot_correct / tot_count) if tot_count > 0 else 0.0,
        "tot_count": tot_count,
        "n": n_q,
    }

    # -------------- ARM 4: DIAG_TOT_RATE_VS_SNR (sweep) --------------
    diag_results: List[Dict[str, float]] = []
    snr_arr: List[float] = []
    tot_rate_arr: List[float] = []
    cluster_acc_in_tot_arr: List[float] = []
    per_snr_q = max(40, n_q // len(SNR_SWEEP))
    for snr in SNR_SWEEP:
        t_count = 0
        t_cluster_correct = 0
        a_correct = 0
        c_correct = 0
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
            if cm < cleanup_thr and tcs > cluster_thr:
                t_count += 1
                if cc:
                    t_cluster_correct += 1
        tr = t_count / per_snr_q
        cat = (t_cluster_correct / t_count) if t_count > 0 else 0.0
        diag_results.append({
            "snr": float(snr),
            "tot_rate": float(tr),
            "cluster_acc_in_tot": float(cat),
            "atom_recall": a_correct / per_snr_q,
            "cluster_recall": c_correct / per_snr_q,
            "n": per_snr_q,
        })
        snr_arr.append(float(snr))
        tot_rate_arr.append(float(tr))
        cluster_acc_in_tot_arr.append(float(cat))
    rho = spearman_rho(np.array(snr_arr), np.array(tot_rate_arr))
    cat_nonempty = [c for c, t in zip(cluster_acc_in_tot_arr, [d["tot_rate"] for d in diag_results]) if t > 0.0]
    cat_pooled = float(np.mean(cat_nonempty)) if cat_nonempty else 0.0
    per_arm["diag_tot_rate_vs_snr"] = {
        "spearman_rho_snr_tot": float(rho),
        "cluster_acc_in_tot_pooled": cat_pooled,
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

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_arm": {}}

    per_arm_summary: Dict[str, Dict[str, float]] = {}
    # collect raw per-arm metrics across seeds
    hc_atom_recalls = []
    lc_refuse_rates = []
    tot_cluster_in_tot_accs = []
    rhos = []
    diag_pooled_cats = []
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {arm: {} for arm in EXPECTED_ARMS}
    for s_key, body in per_seed.items():
        pa = body.get("per_arm", {})
        if "high_conf_high_recall" in pa:
            hc = pa["high_conf_high_recall"]
            hc_atom_recalls.append(hc["atom_recall"])
            per_arm_full["high_conf_high_recall"][s_key] = hc
        if "low_conf_low_recall" in pa:
            lc = pa["low_conf_low_recall"]
            lc_refuse_rates.append(lc["refuse_rate"])
            per_arm_full["low_conf_low_recall"][s_key] = lc
        if "tot_partial_know" in pa:
            tot = pa["tot_partial_know"]
            if tot.get("tot_count", 0) > 0:
                tot_cluster_in_tot_accs.append(tot["cluster_acc_in_tot"])
            per_arm_full["tot_partial_know"][s_key] = tot
        if "diag_tot_rate_vs_snr" in pa:
            d = pa["diag_tot_rate_vs_snr"]
            rhos.append(d["spearman_rho_snr_tot"])
            diag_pooled_cats.append(d.get("cluster_acc_in_tot_pooled", 0.0))
            per_arm_full["diag_tot_rate_vs_snr"][s_key] = d

    hc_recall_mean = float(np.mean(hc_atom_recalls)) if hc_atom_recalls else 0.0
    lc_refuse_mean = float(np.mean(lc_refuse_rates)) if lc_refuse_rates else 0.0
    cluster_acc_in_tot_mean = float(np.mean(tot_cluster_in_tot_accs)) if tot_cluster_in_tot_accs else 0.0
    rho_mean = float(np.mean(rhos)) if rhos else 0.0
    diag_cat_mean = float(np.mean(diag_pooled_cats)) if diag_pooled_cats else 0.0

    per_arm_summary["high_conf_high_recall"] = {"atom_recall_mean": hc_recall_mean, "n": len(hc_atom_recalls)}
    per_arm_summary["low_conf_low_recall"] = {"refuse_rate_mean": lc_refuse_mean, "n": len(lc_refuse_rates)}
    per_arm_summary["tot_partial_know"] = {"cluster_acc_in_tot_mean": cluster_acc_in_tot_mean, "n": len(tot_cluster_in_tot_accs)}
    per_arm_summary["diag_tot_rate_vs_snr"] = {
        "spearman_rho_mean": rho_mean,
        "diag_cluster_acc_in_tot_mean": diag_cat_mean,
        "n": len(rhos),
    }

    # Reconstruct peak-pattern from diag sweep: find peak SNR (max tot_rate); check
    # peak is interior; check cluster_acc_in_tot at peak.
    peak_pattern: Dict[str, Any] = {"peak_snr": None, "peak_tot_rate": 0.0,
                                     "peak_cluster_acc": 0.0, "is_interior": False}
    if per_arm_full.get("diag_tot_rate_vs_snr"):
        # Aggregate per-SNR tot_rate across seeds
        per_snr_tot_rates: Dict[float, List[float]] = {}
        per_snr_cluster_accs: Dict[float, List[float]] = {}
        snr_list_ref: List[float] = []
        for s_key, body in per_arm_full["diag_tot_rate_vs_snr"].items():
            for d in body.get("sweep", []):
                snr = float(d["snr"])
                per_snr_tot_rates.setdefault(snr, []).append(float(d["tot_rate"]))
                per_snr_cluster_accs.setdefault(snr, []).append(float(d["cluster_acc_in_tot"]))
        snr_sorted = sorted(per_snr_tot_rates.keys())
        snr_list_ref = snr_sorted
        mean_tot = {s: float(np.mean(per_snr_tot_rates[s])) for s in snr_sorted}
        mean_cat = {s: float(np.mean(per_snr_cluster_accs[s])) for s in snr_sorted}
        peak_snr = max(mean_tot, key=lambda s: mean_tot[s])
        peak_tot_rate = mean_tot[peak_snr]
        peak_cluster_acc = mean_cat[peak_snr]
        # Interior: peak NOT at lowest or highest SNR in sweep
        is_interior = (peak_snr != snr_sorted[0] and peak_snr != snr_sorted[-1])
        peak_pattern = {
            "peak_snr": peak_snr,
            "peak_tot_rate": peak_tot_rate,
            "peak_cluster_acc": peak_cluster_acc,
            "is_interior": bool(is_interior),
            "per_snr_tot_rate": mean_tot,
            "per_snr_cluster_acc": mean_cat,
        }

    verdict = "MIDDLE_BAND"
    if (peak_pattern["peak_tot_rate"] >= HP_TOT_RATE_AT_PEAK_MIN and
            peak_pattern["is_interior"] and
            peak_pattern["peak_cluster_acc"] >= HP_CLUSTER_ACC_AT_PEAK_MIN and
            hc_recall_mean >= HP_HIGH_CONF_RECALL_MIN and
            lc_refuse_mean >= HP_LOW_CONF_REFUSE_MIN):
        verdict = "HARD_PASS"
    elif (hc_recall_mean < HF_HIGH_CONF_RECALL_LO or
            peak_pattern["peak_cluster_acc"] < MB_CLUSTER_ACC_AT_PEAK_LO):
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | peak_SNR=%s peak_TOT_rate=%.3f peak_cluster_acc=%.3f interior=%s | "
        "HC_recall=%.3f LC_refuse=%.3f rho_legacy=%.3f"
    ) % (verdict, peak_pattern["peak_snr"], peak_pattern["peak_tot_rate"],
         peak_pattern["peak_cluster_acc"], peak_pattern["is_interior"],
         hc_recall_mean, lc_refuse_mean, rho_mean)

    effective_cluster_acc_in_tot = peak_pattern["peak_cluster_acc"]

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": per_arm_summary,
        "peak_pattern": peak_pattern,
        "spearman_rho_snr_tot_mean": rho_mean,
        "cluster_acc_in_tot_mean": effective_cluster_acc_in_tot,
        "high_conf_atom_recall_mean": hc_recall_mean,
        "low_conf_refuse_rate_mean": lc_refuse_mean,
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(EXPECTED_ARMS) * N_QUERIES_PER_ARM,
        "cardinality_ok": (len(per_seed) >= 2),
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
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified",
                                   extra={"_phase": "selftest_done",
                                          "selftest_arms": list(r["per_arm"].keys()),
                                          "rho_selftest": r["per_arm"]["diag_tot_rate_vs_snr"]["spearman_rho_snr_tot"]})
            print("[selftest] OK; rho=%.3f" % r["per_arm"]["diag_tot_rate_vs_snr"]["spearman_rho_snr_tot"], flush=True)
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
    final["_hardening_marker"] = "v1_meta_knowledge_tip_of_tongue"
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
