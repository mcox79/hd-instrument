"""phase_diagram_capacity_codebook_separated_v2a_mech_plus_sentinels --
Rescue Cell A (small/cheap) split from
exp_phase_diagram_capacity_codebook_separated_envelope_v1 per Skunkworks batch 8
2026-06-27 flag-back.

PARENT FINDING (cell v1, Skunkworks per-arm verify off-data):
  - MECH arm: 10 of 10 cells completed at seed=11 (only seed that ran);
    4 of 10 EXCEEDED predicted band (alpha_N in {4.0, 8.0} at both 10x and 2x
    headroom held rec=1.000 vs predicted [0.40, 0.90] floors).
  - KNN_SENTINEL, BARE_E_R, MULTI_BANK arms ALL NaN (OOM at multi-bank K=4
    blew GPU memory budget; sentinel + bare never reached).
  - n_seeds=1 (cardinality breach: planned 3, only 1 fired before halt).

SPLIT-RESCUE RATIONALE (Skunkworks recommendation c+d):
  Cell A (this file): MECH + KNN_SENTINEL + BARE_E_R only; 3 seeds.
                       NO multi-bank (peak W footprint 1.07GB single fp32).
                       Routes remote_cpu_queue (no GPU OOM risk on CPU; ~slower).
  Cell B (sibling):    MULTI_BANK_K4 alone at alpha_N=4 headroom=10x; 3 seeds.
                       Routes overnight_queue (GPU; > 8GB VRAM required).

WHY CHAIN-GRADE-ELIGIBLE (substrate beats baseline at high alpha):
  Parent v1 surface bands were drilled from prior-N studies; substrate
  EXCEEDED bands at 4/10 cells. v2a UPDATES PREDICTED_SURFACE bands to
  embed the observed-substrate-out-performance as new HARD_PASS targets
  (HP_EXCEEDED_BAND_HOLDS): rec_mean >= 0.95 at alpha_N in {4, 8} x
  headroom in {10x, 2x} across 3 seeds replicates the v1 exceed-band
  finding.

  USER BIAS-Q (suspect 1.000): mech-arm rec=1.0 is HONEST_LIFT iff KNN
  sentinel + BARE_E_R also hold their bars at SAME N + V_C regime AND
  substrate sustains across 3 fresh seeds. Cell A satisfies all three.

PER-ARM HP-SCOPE DECLARATION (SCHEMA-VET 5b per exp_dev.md 2026-06-27):
  MECH (envelope band) : HP_ENVELOPE_REC_MIN=0.95 at 10x-headroom alpha<=2
  MECH (exceed band)   : HP_EXCEEDED_REC_MIN=0.95 at alpha in {4,8} headroom in {10x,2x}
  KNN_SENTINEL         : HP_KNN_SENTINEL>=0.95 (sigma=0.10)
  BARE_E_R_ENCODER     : HP_BARE_E_R>=0.99 (bijective lookup)
  MULTI_BANK arm DROPPED (routed to Cell B; Cell A asserts MULTI_BANK==None
  in metrics)

META_RULE_H (cardinality_ok): EXPECTED_N_UNITS = (20 mech + 1 KNN + 1 BARE) * 3 seeds = 66.
META_RULE_J (no silent except): halt loop on any unit exception.
META_RULE_K (smoke fires discriminator): n/a (NO_LOCAL per USER 2026-06-27;
  dispatched direct to remote; selftest + formula assertions are gate).
META_RULE_L (band-floor MIDDLE_BAND): preserved verbatim from v1.

NO LOCAL SMOKE per USER 2026-06-27.

ASCII-only. Single-file. Resumable per-key checkpoint.
Author: exp_dev 2026-06-27 (Skunkworks batch 8 rescue Cell A).
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

import argparse
import atexit
import math
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    list_completed_keys,
)

ANCHOR_NAME = "phase_diagram_capacity_codebook_separated_v2a_mech_plus_sentinels"
_LLM_CALL_COUNTER = [0]
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_capacity_v2a_mech_plus_sentinels"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SMOKE = (RUN_MODE == "smoke")


# Cell A is remote_cpu-routed; GPU not required (no multi-bank arm here).
GPU_AVAIL = torch.cuda.is_available()
if GPU_AVAIL:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_runner"
    GPU_MAX_MEM_GB = 0.0


# Pre-reg bands LOCKED at module init
HP_KNN_SENTINEL = 0.95              # scoped: KNN_SENTINEL arm only
HP_BARE_E_R = 0.99                  # scoped: BARE_E_R_ENCODER arm only
CV_MAX = 0.05
KNN_SENTINEL_SIGMA = 0.10
V_R = 32

# PREDICTED_SURFACE updated to embed parent v1 EXCEEDED-band observations
# (alpha_N >= 4 cells produced rec=1.000 at seed=11; v2a tightens predicted
# upper bound to 1.0 + sets HARD_PASS bar at >=0.95 across 3 seeds).
PREDICTED_SURFACE: Dict[Tuple[float, str], Tuple[float, float]] = {
    (0.5, "10x"):  (0.99, 1.00),
    (0.5, "2x"):   (0.99, 1.00),
    (0.5, "1.0x"): (0.65, 0.75),
    (0.5, "0.5x"): (0.45, 0.55),
    (1.0, "10x"):  (0.99, 1.00),
    (1.0, "2x"):   (0.95, 1.00),
    (1.0, "1.0x"): (0.55, 0.65),
    (1.0, "0.5x"): (0.40, 0.50),
    (2.0, "10x"):  (0.95, 1.00),
    (2.0, "2x"):   (0.85, 0.95),
    (2.0, "1.0x"): (0.45, 0.55),
    (2.0, "0.5x"): (0.30, 0.40),
    # v2a: bands UPDATED per parent v1 exceed-band data
    (4.0, "10x"):  (0.95, 1.00),  # was [0.75, 0.90]; v1 obs=1.000
    (4.0, "2x"):   (0.95, 1.00),  # was [0.60, 0.80]; v1 obs=1.000
    (4.0, "1.0x"): (0.35, 0.45),
    (4.0, "0.5x"): (0.20, 0.30),
    (8.0, "10x"):  (0.95, 1.00),  # was [0.40, 0.65]; v1 obs=1.000
    (8.0, "2x"):   (0.95, 1.00),  # was [0.30, 0.55]; v1 obs=1.000
    (8.0, "1.0x"): (0.20, 0.30),
    (8.0, "0.5x"): (0.15, 0.25),
}

# HARD_PASS_ENVELOPE (low-alpha; preserved from v1)
HP_ENVELOPE_REC_MIN = 0.95
HP_ENVELOPE_ALPHAS = [0.5, 1.0, 2.0]
HP_ENVELOPE_HEADROOM = "10x"

# HARD_PASS_EXCEEDED (NEW v2a; substrate-beats-baseline at high alpha):
# rec_mean >= 0.95 cv<=0.05 at alpha in {4, 8} x headroom in {10x, 2x}
HP_EXCEEDED_REC_MIN = 0.95
HP_EXCEEDED_ALPHAS = [4.0, 8.0]
HP_EXCEEDED_HEADROOMS = ["10x", "2x"]

# HARD_PASS_CODEBOOK (preserved from v1)
HP_CODEBOOK_DELTA = 0.20
HP_CODEBOOK_MIN_MATCHES = 3

V_C_CAP = 200_000

ALPHA_N_AXIS = [0.5, 1.0, 2.0, 4.0, 8.0]
HEADROOM_AXIS = [("10x", 10.0), ("2x", 2.0), ("1.0x", 1.0), ("0.5x", 0.5)]


if SMOKE:
    # Smoke retained for queue_add gate compatibility (does NOT run locally per USER NO-LOCAL).
    N_DIM = 2048
    SEEDS = [11]
    SMOKE_PROBES = [
        ("S1_envelope",  2.0, "10x",  10.0),
        ("S2_codebook",  1.0, "0.5x",  0.5),
        ("S3_baseline",  0.5, "10x",  10.0),
        ("S4_exceeded",  4.0, "10x",  10.0),
    ]
    EXPECTED_N_UNITS = 4 + 1 + 1  # 4 probes + KNN_SENTINEL + BARE_E_R
else:
    N_DIM = 16384
    SEEDS = [11, 13, 19]
    SMOKE_PROBES = []
    n_mech = len(ALPHA_N_AXIS) * len(HEADROOM_AXIS)
    # NO multi-bank in Cell A (routed to Cell B).
    EXPECTED_N_UNITS = (n_mech + 1 + 1) * len(SEEDS)  # 22 * 3 = 66


def _compute_VC_for(alpha_N: float, headroom_val: float, n_dim: int) -> int:
    M = int(round(alpha_N * n_dim))
    target_keys = headroom_val * M
    return int(math.ceil(target_keys / V_R))


def _phase_cells_after_skip(n_dim: int) -> Tuple[List[Tuple[float, str, float, int, int]], List[Dict]]:
    kept = []
    skipped = []
    for alpha_N in ALPHA_N_AXIS:
        M = int(round(alpha_N * n_dim))
        for (h_label, h_val) in HEADROOM_AXIS:
            V_C = _compute_VC_for(alpha_N, h_val, n_dim)
            if V_C > V_C_CAP:
                skipped.append({
                    "alpha_N": alpha_N, "headroom_label": h_label,
                    "headroom_val": h_val, "M": M, "V_C_required": V_C,
                    "skip_reason": "V_C_OVER_LIMIT",
                })
                continue
            kept.append((alpha_N, h_label, h_val, M, V_C))
    return kept, skipped


if not SMOKE:
    _PHASE_CELLS, _SKIP_REGISTRY = _phase_cells_after_skip(N_DIM)
    n_phase_kept = len(_PHASE_CELLS)
    EXPECTED_N_UNITS = (n_phase_kept + 1 + 1) * len(SEEDS)
else:
    _PHASE_CELLS = []
    _SKIP_REGISTRY = []


ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "phaseDiagCapCodebookSeparated-v2a-mechSentinels: N=%d V_R=%d seeds=%s "
    "mode=%s encoder=%s HP_knn=%.2f HP_bare=%.2f CV_max=%.2f "
    "sigma_knn=%.2f HP_env_rec_min=%.2f HP_exc_rec_min=%.2f "
    "HP_cb_delta=%.2f n_alpha=%d n_headroom=%d EXPECTED_N_UNITS=%d "
    "n_phase_kept=%d n_skipped=%d V_C_cap=%d NO_MULTIBANK=Cell_B_routed"
) % (
    N_DIM, V_R, SEEDS, RUN_MODE, ENCODER_PROVENANCE, HP_KNN_SENTINEL,
    HP_BARE_E_R, CV_MAX, KNN_SENTINEL_SIGMA, HP_ENVELOPE_REC_MIN,
    HP_EXCEEDED_REC_MIN, HP_CODEBOOK_DELTA, len(ALPHA_N_AXIS), len(HEADROOM_AXIS),
    EXPECTED_N_UNITS, len(_PHASE_CELLS), len(_SKIP_REGISTRY), V_C_CAP,
)


# ----------------------------- Primitives (verbatim from v1) -----------------------------
def bipolar_t(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_facts(V_C: int, V_R: int, M_facts: int,
                g: np.random.Generator) -> List[Tuple[int, int, int]]:
    max_unique_sr = V_C * V_R
    duplicates_allowed = M_facts > max_unique_sr
    facts = []
    seen_keys: set = set()
    seen_triples: set = set()
    tries = 0
    max_tries = M_facts * 50
    while len(facts) < M_facts and tries < max_tries:
        tries += 1
        s = int(g.integers(0, V_C))
        r = int(g.integers(0, V_R))
        o = int(g.integers(0, V_C))
        if o == s:
            continue
        if duplicates_allowed:
            if (s, r, o) in seen_triples:
                continue
            seen_triples.add((s, r, o))
        else:
            if (s, r) in seen_keys:
                continue
            seen_keys.add((s, r))
        facts.append((s, r, o))
    if len(facts) < M_facts:
        raise RuntimeError("make_facts: only %d/%d at V_C=%d V_R=%d (duplicates_allowed=%s)" % (
            len(facts), M_facts, V_C, V_R, duplicates_allowed))
    return facts


def ingest_hebbian(triples: List[Tuple[int, int, int]],
                    E: torch.Tensor, R: torch.Tensor,
                    sq: float, n_dim: int,
                    batch: int = 1000) -> torch.Tensor:
    W = torch.zeros((n_dim, n_dim), dtype=torch.float32, device=DEVICE)
    if not triples:
        return W
    tr = np.asarray(triples, dtype=np.int64)
    s_idx = torch.from_numpy(tr[:, 0]).to(DEVICE)
    r_idx = torch.from_numpy(tr[:, 1]).to(DEVICE)
    o_idx = torch.from_numpy(tr[:, 2]).to(DEVICE)
    n_total = len(tr)
    for b in range(0, n_total, batch):
        e = min(b + batch, n_total)
        K = E[s_idx[b:e]] * R[r_idx[b:e]] * sq
        V_ = E[o_idx[b:e]]
        W = W + (V_.T @ K) / n_dim
    return W


def eval_recall_at_cell(V_C: int, V_R_arg: int, M_facts: int,
                         n_dim: int, g: np.random.Generator) -> Dict[str, Any]:
    sq = math.sqrt(n_dim)
    E = bipolar_t(V_C, n_dim, g)
    R = bipolar_t(V_R_arg, n_dim, g)
    facts = make_facts(V_C, V_R_arg, M_facts, g)
    keys_unique_mode = "unique_sr" if M_facts <= V_C * V_R_arg else "duplicates_allowed"
    W = ingest_hebbian(facts, E, R, sq, n_dim)

    chunk = min(1000, M_facts)
    hits = 0
    for start in range(0, M_facts, chunk):
        end = min(start + chunk, M_facts)
        batch_facts = facts[start:end]
        s_idx = torch.tensor([f[0] for f in batch_facts], device=DEVICE)
        r_idx = torch.tensor([f[1] for f in batch_facts], device=DEVICE)
        o_idx = torch.tensor([f[2] for f in batch_facts], device=DEVICE)
        keys = E[s_idx] * R[r_idx] * sq
        states = (W @ keys.T).T
        sims = states @ E.T
        preds = sims.argmax(dim=1)
        hits += int((preds == o_idx).sum().item())

    del W, E, R
    if GPU_AVAIL:
        torch.cuda.empty_cache()
    recall = hits / max(M_facts, 1)
    return {"recall_at_1": round(recall, 4), "V_C": V_C, "V_R": V_R_arg,
            "M_facts": M_facts, "N": n_dim, "n_queries": M_facts,
            "alpha_M_over_VC": round(M_facts / max(V_C, 1), 3),
            "alpha_N": round(M_facts / max(n_dim, 1), 3),
            "computed_headroom": round((V_C * V_R_arg) / max(M_facts, 1), 3),
            "keys_unique_mode": keys_unique_mode}


def eval_knn_sentinel(V_C: int, n_dim: int, g: np.random.Generator,
                       noise_sigma: float = KNN_SENTINEL_SIGMA) -> Dict[str, Any]:
    M = min(500, V_C)
    E = bipolar_t(V_C, n_dim, g)
    pick = torch.arange(M, device=DEVICE)
    items = E[pick]
    noise = torch.randn_like(items) * noise_sigma
    noisy = items + noise
    sims = noisy @ E.T
    pred = sims.argmax(dim=1)
    correct = int((pred == pick).sum().item())
    del E, items, noise, noisy, sims, pred
    if GPU_AVAIL:
        torch.cuda.empty_cache()
    return {"recall_at_1": round(correct / max(M, 1), 4),
            "V_C": V_C, "N": n_dim, "noise_sigma": noise_sigma,
            "n_queries": M}


def eval_bare_e_r_encoder(V_C: int, V_R_arg: int, n_dim: int,
                           g: np.random.Generator) -> Dict[str, Any]:
    M = min(500, V_C)
    E = bipolar_t(V_C, n_dim, g)
    pick = torch.arange(M, device=DEVICE)
    queries = E[pick]
    sims = queries @ E.T
    pred = sims.argmax(dim=1)
    correct = int((pred == pick).sum().item())
    del E, queries, sims, pred
    if GPU_AVAIL:
        torch.cuda.empty_cache()
    return {"recall_at_1": round(correct / max(M, 1), 4),
            "V_C": V_C, "V_R": V_R_arg, "N": n_dim, "n_queries": M}


def _bias_s_check(result: Dict[str, Any], target_alpha_N: float,
                   target_headroom: float, n_dim: int) -> None:
    observed_alpha_N = result["alpha_N"]
    if abs(observed_alpha_N - target_alpha_N) >= 0.01:
        raise RuntimeError("BIAS_S_ALPHA_N_DRIFT: observed=%.4f target=%.4f" % (
            observed_alpha_N, target_alpha_N))
    observed_headroom = result["computed_headroom"]
    if target_headroom > 0:
        rel = observed_headroom / target_headroom
        if abs(rel - 1.0) >= 0.05:
            raise RuntimeError("BIAS_S_HEADROOM_DRIFT: observed=%.4f target=%.4f rel=%.4f" % (
                observed_headroom, target_headroom, rel))
    expected_mode = "unique_sr" if target_headroom >= 1.0 else "duplicates_allowed"
    if result["keys_unique_mode"] != expected_mode:
        raise RuntimeError("BIAS_S_KEY_MODE_MISMATCH: observed=%s expected=%s" % (
            result["keys_unique_mode"], expected_mode))


# ----------------------------- self-test -----------------------------
def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V_R_t = V_R
    V_C_t = 200
    M_t = 100

    E = bipolar_t(V_C_t, n, g)
    R = bipolar_t(V_R_t, n, g)
    assert E.shape == (V_C_t, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    facts_low = make_facts(V_C_t, V_R_t, 100, g)
    assert len(facts_low) == 100
    keys_low = set((s, r) for s, r, _ in facts_low)
    assert len(keys_low) == 100

    g3 = np.random.default_rng(1)
    facts_high = make_facts(10, 4, 50, g3)
    assert len(facts_high) == 50

    g4 = np.random.default_rng(2)
    out = eval_recall_at_cell(V_C_t, V_R_t, M_t, n, g4)
    assert 0.0 <= out["recall_at_1"] <= 1.0
    assert out["alpha_N"] == round(M_t / n, 3)
    assert out["keys_unique_mode"] == "unique_sr"

    g5 = np.random.default_rng(3)
    knn = eval_knn_sentinel(V_C_t, n, g5, noise_sigma=0.10)
    assert knn["recall_at_1"] >= 0.95, "T5 KNN %.3f < 0.95" % knn["recall_at_1"]

    g6 = np.random.default_rng(4)
    bare = eval_bare_e_r_encoder(V_C_t, V_R_t, n, g6)
    assert bare["recall_at_1"] >= 0.99, "T6 BARE %.3f < 0.99" % bare["recall_at_1"]

    # BIAS-S regime checks
    fake_ok = {"alpha_N": 1.0, "computed_headroom": 10.0, "keys_unique_mode": "unique_sr"}
    _bias_s_check(fake_ok, 1.0, 10.0, n)
    for bad, msg_part in (
        ({"alpha_N": 1.1, "computed_headroom": 10.0,
          "keys_unique_mode": "unique_sr"}, "BIAS_S_ALPHA_N_DRIFT"),
        ({"alpha_N": 1.0, "computed_headroom": 0.5,
          "keys_unique_mode": "duplicates_allowed"}, "BIAS_S_HEADROOM_DRIFT"),
        ({"alpha_N": 1.0, "computed_headroom": 10.0,
          "keys_unique_mode": "duplicates_allowed"}, "BIAS_S_KEY_MODE_MISMATCH"),
    ):
        try:
            _bias_s_check(bad, 1.0, 10.0, n)
            raise AssertionError("%s not raised" % msg_part)
        except RuntimeError as e:
            assert msg_part in str(e)

    assert HP_KNN_SENTINEL == 0.95
    assert HP_BARE_E_R == 0.99
    assert CV_MAX == 0.05
    assert KNN_SENTINEL_SIGMA == 0.10
    assert V_R == 32
    assert _LLM_CALL_COUNTER[0] == 0

    if not SMOKE:
        assert len(_PHASE_CELLS) == 20, "expected 20 phase cells; got %d" % len(_PHASE_CELLS)
        assert len(_SKIP_REGISTRY) == 0, "expected 0 SKIPs"
        # Cell A: 20 mech + 1 KNN + 1 BARE per seed = 22; * 3 seeds = 66 (NO multi-bank)
        assert EXPECTED_N_UNITS == 66, "EXPECTED_N_UNITS=%d != 66 (Cell A is mech+sentinels only)" % EXPECTED_N_UNITS
    else:
        # Smoke: 4 probes (env, codebook, baseline, exceeded) + 1 KNN + 1 BARE = 6
        assert EXPECTED_N_UNITS == 6, "smoke EXPECTED_N_UNITS=%d != 6" % EXPECTED_N_UNITS

    for alpha in ALPHA_N_AXIS:
        for h_label, _ in HEADROOM_AXIS:
            assert (alpha, h_label) in PREDICTED_SURFACE, (
                "PREDICTED_SURFACE missing (%.1f, %s)" % (alpha, h_label))

    # v2a-specific: assert exceeded-band updates are present
    for alpha in HP_EXCEEDED_ALPHAS:
        for h_label in HP_EXCEEDED_HEADROOMS:
            lo, hi = PREDICTED_SURFACE[(alpha, h_label)]
            assert lo >= HP_EXCEEDED_REC_MIN, (
                "v2a EXCEEDED_BAND_NOT_TIGHTENED: (%.1f, %s) lo=%.3f < HP=%.2f" % (
                    alpha, h_label, lo, HP_EXCEEDED_REC_MIN))

    print(("[selftest] PASS unique_sr_rec=%.3f knn=%.3f bare=%.3f n_phase=%d "
           "EXPECTED_N_UNITS=%d gpu=%s") % (
        out["recall_at_1"], knn["recall_at_1"], bare["recall_at_1"],
        len(_PHASE_CELLS), EXPECTED_N_UNITS, GPU_AVAIL), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------- run_unit + main -----------------------------
_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time(),
                                    "failures": []}


def _fmt_alpha(a: float) -> str:
    return ("%.1f" % a).replace(".", "p")


def _build_keys() -> List[str]:
    keys = []
    for s in SEEDS:
        if SMOKE:
            for (probe_name, alpha_N, h_label, h_val) in SMOKE_PROBES:
                keys.append("seed%d_armSMOKE_%s_alpha%s_headroom%s" % (
                    s, probe_name, _fmt_alpha(alpha_N), h_label))
        else:
            for (alpha_N, h_label, h_val, M, V_C) in _PHASE_CELLS:
                keys.append("seed%d_armMECH_alpha%s_headroom%s" % (
                    s, _fmt_alpha(alpha_N), h_label))
        keys.append("seed%d_armKNN_SENTINEL" % s)
        keys.append("seed%d_armBARE_E_R" % s)
    return keys


def _parse_key(key: str) -> Dict[str, Any]:
    parts = key.split("_")
    seed = int(parts[0].replace("seed", ""))
    if "armMECH" in key:
        alpha_str = key.split("_alpha")[1].split("_headroom")[0]
        h_label = key.split("_headroom")[1]
        return {"seed": seed, "arm": "MECH",
                "alpha_N": float(alpha_str.replace("p", ".")),
                "headroom_label": h_label}
    if "armKNN_SENTINEL" in key:
        return {"seed": seed, "arm": "KNN_SENTINEL"}
    if "armBARE_E_R" in key:
        return {"seed": seed, "arm": "BARE_E_R"}
    if "armSMOKE" in key:
        probe_name = key.split("_armSMOKE_")[1].split("_alpha")[0]
        alpha_str = key.split("_alpha")[1].split("_headroom")[0]
        h_label = key.split("_headroom")[1]
        return {"seed": seed, "arm": "SMOKE", "probe_name": probe_name,
                "alpha_N": float(alpha_str.replace("p", ".")),
                "headroom_label": h_label}
    raise ValueError("unparseable key: %s" % key)


def _headroom_val_for(h_label: str) -> float:
    for (lab, val) in HEADROOM_AXIS:
        if lab == h_label:
            return val
    for (_, _, lab2, val2) in SMOKE_PROBES:
        if lab2 == h_label:
            return val2
    raise ValueError("unknown headroom label: %s" % h_label)


def run_unit(parsed: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.time()
    seed = parsed["seed"]
    arm = parsed["arm"]
    g = np.random.default_rng(seed * 100003 + hash(arm) % 100003)
    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    if arm == "KNN_SENTINEL":
        rec = eval_knn_sentinel(max(2000, 4000), N_DIM, g,
                                 noise_sigma=KNN_SENTINEL_SIGMA)
        out = {
            "seed": seed, "arm": arm,
            "recall_at_1": rec["recall_at_1"],
            "noise_sigma": rec["noise_sigma"],
            "n_queries": rec["n_queries"],
            "wall_s": round(time.time() - t0, 2),
            "run_mode": RUN_MODE,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
    elif arm == "BARE_E_R":
        rec = eval_bare_e_r_encoder(max(2000, 4000), V_R, N_DIM, g)
        out = {
            "seed": seed, "arm": arm,
            "recall_at_1": rec["recall_at_1"],
            "V_C": rec["V_C"], "V_R": rec["V_R"], "N": rec["N"],
            "n_queries": rec["n_queries"],
            "wall_s": round(time.time() - t0, 2),
            "run_mode": RUN_MODE,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
    elif arm == "MECH" or arm == "SMOKE":
        alpha_N = parsed["alpha_N"]
        h_label = parsed["headroom_label"]
        h_val = _headroom_val_for(h_label)
        M = int(round(alpha_N * N_DIM))
        V_C = _compute_VC_for(alpha_N, h_val, N_DIM)
        target_headroom = h_val
        if V_C > V_C_CAP:
            raise RuntimeError("UNEXPECTED_SKIP_AT_RUNTIME: V_C=%d > cap=%d for alpha_N=%.2f headroom=%s" % (
                V_C, V_C_CAP, alpha_N, h_label))
        rec = eval_recall_at_cell(V_C, V_R, M, N_DIM, g)
        _bias_s_check(rec, alpha_N, target_headroom, N_DIM)
        out = {
            "seed": seed, "arm": arm,
            "alpha_N_target": alpha_N, "headroom_label": h_label,
            "headroom_target": target_headroom,
            **rec,
            "wall_s": round(time.time() - t0, 2),
            "run_mode": RUN_MODE,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        if arm == "SMOKE":
            out["probe_name"] = parsed["probe_name"]
    else:
        raise RuntimeError("unknown arm: %s" % arm)

    if GPU_AVAIL:
        out["peak_mem_mb"] = int(torch.cuda.max_memory_allocated(DEVICE) / 1024 / 1024)
    else:
        out["peak_mem_mb"] = 0
    return out


def compute_verdict(per_key: Dict[str, Dict],
                     failures: List[Dict] = None) -> Tuple[str, str, Dict]:
    if failures is None:
        failures = []
    if not per_key and not failures:
        return ("HARD_FAIL", "no_units", {})

    n_units_observed = len(per_key)
    cardinality_ok = (n_units_observed >= EXPECTED_N_UNITS)

    sentinel_recs = [float(v["recall_at_1"]) for v in per_key.values()
                      if v.get("arm") == "KNN_SENTINEL"]
    knn_mean = float(np.mean(sentinel_recs)) if sentinel_recs else float("nan")
    knn_ok = (not math.isnan(knn_mean)) and (knn_mean >= HP_KNN_SENTINEL)

    bare_recs = [float(v["recall_at_1"]) for v in per_key.values()
                  if v.get("arm") == "BARE_E_R"]
    bare_mean = float(np.mean(bare_recs)) if bare_recs else float("nan")
    bare_ok = (not math.isnan(bare_mean)) and (bare_mean >= HP_BARE_E_R)

    surface: Dict[str, Dict] = {}
    by_cell: Dict[Tuple[float, str], List[float]] = {}
    for v in per_key.values():
        if v.get("arm") != "MECH":
            continue
        key = (float(v["alpha_N_target"]), str(v["headroom_label"]))
        by_cell.setdefault(key, []).append(float(v["recall_at_1"]))
    for (alpha_N, h_label), recs in by_cell.items():
        m = float(np.mean(recs))
        s = float(np.std(recs)) if len(recs) > 1 else 0.0
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else 0.0
        pred = PREDICTED_SURFACE.get((alpha_N, h_label), (None, None))
        in_band = (pred[0] is not None
                    and pred[0] - 0.05 <= m <= pred[1] + 0.05)
        surface["alpha%s_headroom%s" % (_fmt_alpha(alpha_N), h_label)] = {
            "alpha_N": alpha_N, "headroom_label": h_label,
            "recall_mean": round(m, 4),
            "recall_cv": round(cv, 4),
            "n_seeds_observed": len(recs),
            "recall_per_seed": [round(r, 4) for r in recs],
            "predicted_band": list(pred),
            "in_predicted_band": in_band,
        }

    n_llm = sum(int(b.get("_llm_forward_calls_at_inference", 0))
                 for b in per_key.values())
    substrate_only_ok = (n_llm == 0)

    # HP_ENVELOPE (low-alpha)
    env_cells_pass = []
    env_cells_fail = []
    for alpha in HP_ENVELOPE_ALPHAS:
        k = "alpha%s_headroom%s" % (_fmt_alpha(alpha), HP_ENVELOPE_HEADROOM)
        if k in surface:
            st = surface[k]
            if st["recall_mean"] >= HP_ENVELOPE_REC_MIN and st["recall_cv"] <= CV_MAX:
                env_cells_pass.append(k)
            else:
                env_cells_fail.append(k)
    envelope_pass = (len(env_cells_pass) >= 3)

    # HP_EXCEEDED (NEW v2a; high-alpha substrate-beats-baseline)
    exc_cells_pass = []
    exc_cells_fail = []
    for alpha in HP_EXCEEDED_ALPHAS:
        for h_label in HP_EXCEEDED_HEADROOMS:
            k = "alpha%s_headroom%s" % (_fmt_alpha(alpha), h_label)
            if k in surface:
                st = surface[k]
                if st["recall_mean"] >= HP_EXCEEDED_REC_MIN and st["recall_cv"] <= CV_MAX:
                    exc_cells_pass.append(k)
                else:
                    exc_cells_fail.append(k)
    n_exc_required = len(HP_EXCEEDED_ALPHAS) * len(HP_EXCEEDED_HEADROOMS)
    exceeded_pass = (len(exc_cells_pass) == n_exc_required)

    # HP_CODEBOOK
    cb_matches = 0
    cb_details: List[str] = []
    for alpha in ALPHA_N_AXIS:
        k_10 = "alpha%s_headroom10x" % _fmt_alpha(alpha)
        k_1 = "alpha%s_headroom1.0x" % _fmt_alpha(alpha)
        k_05 = "alpha%s_headroom0.5x" % _fmt_alpha(alpha)
        if all(k in surface for k in (k_10, k_1, k_05)):
            ref = surface[k_10]["recall_mean"]
            d1 = ref - surface[k_1]["recall_mean"]
            d05 = ref - surface[k_05]["recall_mean"]
            if d1 >= HP_CODEBOOK_DELTA and d05 >= HP_CODEBOOK_DELTA:
                cb_matches += 1
                cb_details.append("alpha%.1f: d1=%.3f d0.5=%.3f" % (alpha, d1, d05))
    codebook_pass = (cb_matches >= HP_CODEBOOK_MIN_MATCHES)

    summ_rows = []
    for k in sorted(surface.keys()):
        st = surface[k]
        summ_rows.append("%s[rec=%.4f cv=%.4f n=%d pred=%s in_band=%s]" % (
            k, st["recall_mean"], st["recall_cv"], st["n_seeds_observed"],
            st["predicted_band"], st["in_predicted_band"]))
    summ = " | ".join(summ_rows) if summ_rows else "no_mech_cells"
    summ += " | KNN=%.4f (>=%.2f %s)" % (knn_mean, HP_KNN_SENTINEL,
                                           "OK" if knn_ok else "FAIL")
    summ += " | BARE_E_R=%.4f (>=%.2f %s)" % (bare_mean, HP_BARE_E_R,
                                                "OK" if bare_ok else "FAIL")
    card_str = " | n_units=%d/expected=%d (%s)" % (
        n_units_observed, EXPECTED_N_UNITS,
        "OK" if cardinality_ok else "BREACH_META_RULE_H")
    fail_str = ""
    if failures:
        fail_str = " | failures=%d [%s]" % (
            len(failures),
            "; ".join("%s:%s" % (f.get("key", "?"), f.get("exc_type", "?"))
                       for f in failures[:3]))

    detail = {
        "surface": surface,
        "knn_sentinel_mean": knn_mean,
        "knn_sentinel_ok": knn_ok,
        "bare_e_r_mean": bare_mean,
        "bare_e_r_ok": bare_ok,
        "multi_bank_probe_mean": None,
        "envelope_cells_pass": env_cells_pass,
        "envelope_cells_fail": env_cells_fail,
        "envelope_pass": envelope_pass,
        "exceeded_cells_pass": exc_cells_pass,
        "exceeded_cells_fail": exc_cells_fail,
        "exceeded_pass": exceeded_pass,
        "codebook_matches": cb_matches,
        "codebook_details": cb_details,
        "codebook_pass": codebook_pass,
        "substrate_only_ok": substrate_only_ok,
        "n_llm_calls": int(n_llm),
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "skip_registry": _SKIP_REGISTRY,
        "failures": failures,
    }

    if SMOKE:
        probes_by_name = {}
        for v in per_key.values():
            if v.get("arm") == "SMOKE":
                probes_by_name[v["probe_name"]] = float(v["recall_at_1"])
        s1 = probes_by_name.get("S1_envelope", float("nan"))
        s2 = probes_by_name.get("S2_codebook", float("nan"))
        s3 = probes_by_name.get("S3_baseline", float("nan"))
        s4 = probes_by_name.get("S4_exceeded", float("nan"))
        smoke_ok = (s1 >= 0.90 and s3 >= 0.99 and 0.35 <= s2 <= 0.55
                    and s4 >= 0.90)
        smoke_summ = ("S1_env=%.4f (>=0.90) S2_cb=%.4f (0.35-0.55) "
                       "S3_base=%.4f (>=0.99) S4_exc=%.4f (>=0.90)") % (s1, s2, s3, s4)
        if substrate_only_ok and smoke_ok and not failures and cardinality_ok and knn_ok and bare_ok:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: discriminator fires per Cell A v2a smoke | %s | %s%s" % (
                        smoke_summ, summ, card_str),
                    detail)
        return ("HARD_FAIL",
                "SMOKE_FAIL | %s | %s%s%s" % (
                    smoke_summ, summ, card_str, fail_str),
                detail)

    if failures:
        return ("HARD_FAIL",
                "HARD_FAIL_UNIT_EXCEPTION: %d units raised exceptions (META_RULE_J) | %s%s%s" % (
                    len(failures), summ, card_str, fail_str),
                detail)
    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: n_units=%d < expected=%d | %s%s" % (
                    n_units_observed, EXPECTED_N_UNITS, summ, card_str),
                detail)
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_SUBSTRATE_ONLY: %d LLM calls | %s%s" % (n_llm, summ, card_str),
                detail)
    if not knn_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_SCOPED_HP_KNN_SENTINEL: %.4f < %.2f (scoped; mechanism arms exempt) | %s%s" % (
                    knn_mean, HP_KNN_SENTINEL, summ, card_str),
                detail)
    if not bare_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_SCOPED_HP_BARE_E_R: %.4f < %.2f (scoped; mechanism arms exempt) | %s%s" % (
                    bare_mean, HP_BARE_E_R, summ, card_str),
                detail)

    if envelope_pass and exceeded_pass and codebook_pass:
        return ("CHAIN_GRADE_TRIO",
                "CHAIN_GRADE_TRIO: envelope HP (%d/3) + exceeded HP (%d/%d substrate-beats-baseline) + codebook separation (%d matched alphas) | %s%s" % (
                    len(env_cells_pass), len(exc_cells_pass), n_exc_required,
                    cb_matches, summ, card_str),
                detail)
    if envelope_pass and exceeded_pass:
        return ("CHAIN_GRADE_BOTH",
                "CHAIN_GRADE_BOTH: envelope HP (%d/3) + exceeded HP (%d/%d) | codebook=%d matched | %s%s" % (
                    len(env_cells_pass), len(exc_cells_pass), n_exc_required,
                    cb_matches, summ, card_str),
                detail)
    if envelope_pass and codebook_pass:
        return ("CHAIN_GRADE_ENV_CB",
                "CHAIN_GRADE_ENV_CB: envelope HP + codebook | exceeded=%d/%d (failed: %s) | %s%s" % (
                    len(exc_cells_pass), n_exc_required,
                    ",".join(exc_cells_fail), summ, card_str),
                detail)
    if exceeded_pass:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_EXCEEDED_ONLY: exceeded HP (%d/%d) but envelope=%d/3 OR codebook=%d/%d | %s%s" % (
                    len(exc_cells_pass), n_exc_required, len(env_cells_pass),
                    cb_matches, HP_CODEBOOK_MIN_MATCHES, summ, card_str),
                detail)
    if envelope_pass:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_ENVELOPE_ONLY: envelope HP but exceeded=%d/%d codebook=%d/%d | %s%s" % (
                    len(env_cells_pass), n_exc_required,
                    cb_matches, HP_CODEBOOK_MIN_MATCHES, summ, card_str),
                detail)
    if codebook_pass:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_CODEBOOK_ONLY: codebook | envelope=%d/3 exceeded=%d/%d | %s%s" % (
                    len(env_cells_pass), len(exc_cells_pass), n_exc_required,
                    summ, card_str),
                detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_NO_HP: envelope=%d/3 exceeded=%d/%d codebook=%d/%d (META_RULE_L band-floor) | %s%s" % (
                len(env_cells_pass), len(exc_cells_pass), n_exc_required,
                cb_matches, HP_CODEBOOK_MIN_MATCHES, summ, card_str),
            detail)


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        run_config = {"N": N_DIM, "run_mode": RUN_MODE}
        keys = _build_keys()
        agg = aggregate_partials(od, seeds=keys, run_config=run_config)
        if not agg and not _RESULTS_HOLDER["failures"]:
            return
        v, vmsg, detail = compute_verdict(agg, _RESULTS_HOLDER["failures"])
        metrics = _build_metrics(v, vmsg, detail, list(agg.values()),
                                  atexit_synth=True)
        write_metrics(od, metrics, results=list(agg.values()))
        print("[atexit] wrote synth metrics.json (%d units)" % len(agg), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


def _build_metrics(v: str, vmsg: str, detail: Dict, units: List[Dict],
                    atexit_synth: bool = False) -> Dict:
    return {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
        "n_units": len(units),
        "n_units_expected": EXPECTED_N_UNITS,
        "cardinality_ok": (len(units) >= EXPECTED_N_UNITS),
        "n_failures": len(_RESULTS_HOLDER["failures"]),
        "failures": _RESULTS_HOLDER["failures"],
        "config_version": CONFIG_VERSION,
        "N_DIM": N_DIM,
        "V_R": V_R,
        "ALPHA_N_AXIS": ALPHA_N_AXIS,
        "HEADROOM_AXIS": [list(h) for h in HEADROOM_AXIS],
        "PREDICTED_SURFACE": {("%.1f_%s" % (a, h)): list(b)
                               for (a, h), b in PREDICTED_SURFACE.items()},
        "HP_KNN_SENTINEL": HP_KNN_SENTINEL,
        "HP_BARE_E_R": HP_BARE_E_R,
        "HP_ENVELOPE_REC_MIN": HP_ENVELOPE_REC_MIN,
        "HP_EXCEEDED_REC_MIN": HP_EXCEEDED_REC_MIN,
        "HP_EXCEEDED_ALPHAS": HP_EXCEEDED_ALPHAS,
        "HP_EXCEEDED_HEADROOMS": HP_EXCEEDED_HEADROOMS,
        "HP_CODEBOOK_DELTA": HP_CODEBOOK_DELTA,
        "HP_CODEBOOK_MIN_MATCHES": HP_CODEBOOK_MIN_MATCHES,
        "CV_MAX": CV_MAX,
        "KNN_SENTINEL_SIGMA": KNN_SENTINEL_SIGMA,
        "HP_SCOPE": {
            "MECH_envelope": ["HP_ENVELOPE_REC_MIN>=%.2f at alpha<=2 headroom=10x" % HP_ENVELOPE_REC_MIN],
            "MECH_exceeded": ["HP_EXCEEDED_REC_MIN>=%.2f at alpha in {4,8} headroom in {10x,2x}" % HP_EXCEEDED_REC_MIN],
            "KNN_SENTINEL": ["HP_KNN_SENTINEL>=%.2f" % HP_KNN_SENTINEL],
            "BARE_E_R": ["HP_BARE_E_R>=%.2f" % HP_BARE_E_R],
            "SMOKE": [],
        },
        "seeds": SEEDS,
        "per_unit": units,
        "detail": detail,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg[:300],
        "_atexit_synth": atexit_synth,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "gpu_max_mem_gb": GPU_MAX_MEM_GB,
        "corpus_provenance": CORPUS_PROVENANCE,
        "allow_synthetic": True,
        "metrics_source": "measured_substrate_bipolar_hebbian_W_capacity_v2a_mech_plus_sentinels",
        "DESIGN_NOTE": (
            "CAPACITY_V2A_MECH_PLUS_SENTINELS: Rescue Cell A split from v1 per "
            "Skunkworks batch 8. MECH (20 cells) + KNN_SENTINEL + BARE_E_R only; "
            "MULTI_BANK arm DROPPED (routed to Cell B GPU). 3 seeds (was 1). "
            "PREDICTED_SURFACE bands UPDATED to embed v1 substrate-beats-baseline "
            "exceed observations at alpha in {4,8} headroom in {10x,2x}. HARD_PASS "
            "TRIO requires envelope + exceeded + codebook all pass. Per-arm HP "
            "scope declared (SCHEMA-VET 5b). Routes remote_cpu_queue per USER "
            "NO_LOCAL 2026-06-27."
        ),
    }


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_R=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_R, CONFIG_VERSION), flush=True)
    print("[device] avail=%s name=%s mem_gb=%.1f" % (GPU_AVAIL, GPU_NAME, GPU_MAX_MEM_GB),
          flush=True)
    print("[cardinality] expected_n_units=%d (META_RULE_H guard)" % EXPECTED_N_UNITS,
          flush=True)
    if _SKIP_REGISTRY:
        print("[skip_registry] %d cells skipped: %s" % (
            len(_SKIP_REGISTRY), _SKIP_REGISTRY), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    all_keys = _build_keys()
    done_keys = set(list_completed_keys(out_dir, run_config=run_config))
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(all_keys)), flush=True)

    halt_after_loop = False
    for key in all_keys:
        if key in done_keys:
            continue
        try:
            parsed = _parse_key(key)
            print("  [run] %s ..." % key, flush=True)
            rec = run_unit(parsed)
            write_partial_key(out_dir, key, rec)
            print("  [done] %s rec=%.4f wall=%.1fs peak=%dMB" % (
                key, rec["recall_at_1"], rec["wall_s"],
                rec.get("peak_mem_mb", 0)), flush=True)
        except Exception as e:
            tb = traceback.format_exc()
            fail_entry = {
                "key": key,
                "exc_type": type(e).__name__,
                "exc_msg": str(e)[:500],
                "traceback": tb[-2000:],
            }
            _RESULTS_HOLDER["failures"].append(fail_entry)
            print("[UNIT_EXCEPTION] %s type=%s msg=%r" % (
                key, type(e).__name__, str(e)[:200]), flush=True)
            print("[TRACEBACK]\n%s" % tb, flush=True)
            print("[META_RULE_J] halting loop on unit exception (no silent-continue)", flush=True)
            halt_after_loop = True
            break

    agg = aggregate_partials(out_dir, seeds=all_keys, run_config=run_config)
    units = [agg[k] for k in all_keys if k in agg]
    failures = _RESULTS_HOLDER["failures"]

    if not units and not failures:
        print("[FATAL] no partials available + no failures", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0

    v, vmsg, detail = compute_verdict(agg, failures)
    print("\n[VERDICT] %s" % v, flush=True)
    print("[VERDICT_MSG] %s" % vmsg, flush=True)

    metrics = _build_metrics(v, vmsg, detail, units, atexit_synth=False)
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %d failures, %.1fs)" % (
        len(units), len(failures), metrics["elapsed_s"]), flush=True)
    if halt_after_loop:
        sys.exit(1)
