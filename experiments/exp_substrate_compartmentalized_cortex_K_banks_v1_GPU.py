"""substrate_compartmentalized_cortex_K_banks_v1_GPU.

Stage 2 NREM rescue cell C. Tests COMPARTMENTALIZED CORTEX (multi-bank) as
rescue for Hc CORTEX_WRITE_SATURATION (confirmed at hippo_bottleneck v2,
commit c374d74f).

CITED@brain_lit_modular_cortex_columns: cortex is modular — visual/motor/
language regions consolidate independently from different hippocampal
subfields; one undifferentiated dense cortex saturates; compartments do not.

LINEAGE:
  Hippo bottleneck v2 MEASURED@d:/AI/hd-instrument/data/exp_substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2/metrics.json:
    R_DIRECT=0.985, R_STANDARD=0.219, R_CLEAN_VALS_TO_CORTEX=0.985
  Hc = cortex write saturation IS a write-saturation mechanism class.
  Rescue: route writes into K separate cortex banks instead of 1 large W.

HYPOTHESIS:
  THEORETICAL@cortex_write_saturation_partition: single W_c (N_c,N_c) writes
  M outer products into one matrix. Saturation ~ M / capacity(N_c).
  K-bank rescue: each item routed to bank k=hash(cue) mod K; per-bank load
  M/K. Bank capacity proportional to N_c^2 (Hopfield-like). Per-bank saturation
  drops by factor 1/K. At K=10 with M=8192, per-bank load is 819 -> well
  inside per-bank capacity, recall should approach DIRECT ceiling 0.985.

ARMS (5; META_RULE_AF distinct W_cortex hashes per arm via different
routing/bank-count):
  ARM_STANDARD_K1          -- baseline: 1 big cortex W (reproduces v2 STANDARD ~0.22)
  ARM_COMPARTMENT_K2       -- 2 banks; deterministic hash routing
  ARM_COMPARTMENT_K5       -- 5 banks
  ARM_COMPARTMENT_K10      -- 10 banks (brain-realistic K)
  ARM_COMPARTMENT_K20      -- 20 banks (saturation rescue limit)

PRE-REG BANDS:
  HARD_PASS: ARM_COMPARTMENT_K10 (or K20) recall >= R_STANDARD + 0.50
             (substantial closure of v2 measured gap 0.766).
  MIDDLE_BAND: best COMPARTMENT recall in (R_STANDARD+0.10, R_STANDARD+0.50]
  HARD_FAIL: no COMPARTMENT >= R_STANDARD + 0.10 (rescue does not work)

CARDINALITY: 5 arms * 3 seeds = 15 (FULL); 5 * 1 = 5 (SMOKE).
SWEEP cardinality_ok mandatory pre-reg (META_RULE_H).

REGIME (matches v2):
  FULL:  M=2048, N_h=8192, N_c=2048; alpha_simple=0.25; seeds=[7,17,23]
  SMOKE: M=512, N_h=2048, N_c=512; alpha_simple=0.25; seed=[7]

DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at SAME alpha as full; v2 gap=0.40
at smoke vs 0.77 at full; rescue should LIFT at both regimes if mechanism real.

ATOMICITY: tmp+os.replace at final metrics write (META_RULE_AH).

ASCII-only. PROT-020: imports torch. Routes to overnight_queue (GPU).
PRESERVE_ENV_VARS: HDLAB_QUEUE
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch  # PROT-020 GPU queue routing gate

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "substrate_compartmentalized_cortex_K_banks_v1_GPU"
_HARDENING_MARKER = "v1_COMPARTMENT_K1_K2_K5_K10_K20"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")

RUN_MODE = (
    "smoke"
    if (_ARGS.smoke or _NAME_SAYS_SMOKE
        or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke")
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# Config (matches v2 reference: alpha_simple=0.25; M=2048 N_h=8192 N_c=2048).
M_ITEMS_FULL = 2048
N_HIPPO_FULL = 8192
N_CORTEX_FULL = 2048
SEEDS_FULL = [7, 17, 23]

M_ITEMS_SMOKE = 512
N_HIPPO_SMOKE = 2048
N_CORTEX_SMOKE = 512
SEEDS_SMOKE = [7]

if RUN_MODE == "smoke":
    M_ITEMS = M_ITEMS_SMOKE
    N_HIPPO = N_HIPPO_SMOKE
    N_CORTEX = N_CORTEX_SMOKE
    SEEDS = SEEDS_SMOKE
else:
    M_ITEMS = M_ITEMS_FULL
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    SEEDS = SEEDS_FULL

HIPPO_SPARSITY_SPARSE = 0.10
ETA_CORTEX = 0.005
N_REPLAY_PER_ITEM = 1

K_BANK_VALUES: Tuple[int, ...] = (1, 2, 5, 10, 20)
ARM_NAMES: Tuple[str, ...] = tuple(
    f"ARM_COMPARTMENT_K{k}" if k > 1 else "ARM_STANDARD_K1"
    for k in K_BANK_VALUES
)
EXPECTED_N_UNITS = len(ARM_NAMES) * len(SEEDS)

HARD_PASS_LIFT_MIN = 0.50
MIDDLE_BAND_LIFT_MIN = 0.10


def _alpha_simple(M: int, N_h: int) -> float:
    return float(M) / float(N_h)


def _select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


DEVICE = _select_device()
DTYPE = torch.float32

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},M={M_ITEMS},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"alpha_simple={_alpha_simple(M_ITEMS, N_HIPPO):.3f},"
    f"K_BANK={K_BANK_VALUES},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},DEVICE={DEVICE.type},"
    f"hardening=METARULE_AF+METARULE_AH+METARULE_H+COMPARTMENT_K_SWEEP"
)


def _heartbeat_write(out_dir: Path, unit_idx: int, total_units: int,
                     elapsed_s: float, extra: Dict = None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units),
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra:
        row["extra"] = extra
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        with (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


def _l2_normalize(x: torch.Tensor, dim: int = -1) -> torch.Tensor:
    n = torch.linalg.vector_norm(x, dim=dim, keepdim=True)
    return x / torch.clamp(n, min=1e-12)


def _sparse_dg(x: torch.Tensor, P: torch.Tensor, k: int) -> torch.Tensor:
    h_raw = x @ P.t()
    abs_h = h_raw.abs()
    topk_idx = torch.topk(abs_h, k, dim=1, largest=True).indices
    signs = torch.sign(h_raw.gather(1, topk_idx))
    signs = torch.where(signs == 0, torch.ones_like(signs), signs)
    out = torch.zeros_like(h_raw)
    out.scatter_(1, topk_idx, signs)
    return out


def _arm_hash(arm_name: str, W_or_list) -> str:
    """Hash a deterministic slice of cortex bank(s)."""
    if isinstance(W_or_list, list):
        # Multi-bank: concat first slice of bank-0.
        sample = W_or_list[0][:4, :64].detach().cpu().to(torch.float64).numpy()
    else:
        sample = W_or_list[:4, :64].detach().cpu().to(torch.float64).numpy()
    blob = arm_name.encode("ascii") + sample.tobytes()
    return hashlib.sha256(blob).hexdigest()[:16]


def _route_to_bank(cue_idx: torch.Tensor, K: int) -> torch.Tensor:
    """Deterministic hash routing: item i -> bank (i % K).

    Uses item-index modulo K (not content hash) for stable, balanced routing.
    Each item lands in exactly one bank.
    """
    return cue_idx % K


def run_arm(arm_name: str, K_banks: int, seed: int,
            keys_raw: torch.Tensor, vals_raw: torch.Tensor,
            P_in: torch.Tensor, P_hc: torch.Tensor,
            out_dir: Path) -> Dict:
    """One arm: K-bank compartmentalized cortex.

    Pipeline:
      1. Encode keys/vals via sparse-DG -> keys_h, vals_h
      2. Hippo Hebbian write (STANDARD): W_h = vals_h.T @ keys_h
      3. Replay: cues_h = keys_h[perm]; noisy hippo readout -> vals_c_react
      4. Compartment write: per item i, write to bank b = i % K:
           W_c_bank[b] += eta * vals_c_react[i] outer cues_c[i]
      5. Recall: per query keys_c[i], compute bank b=i%K, preds = sign(keys_c[i] @ W_c_bank[b].T);
         compare argmax over vals_c.

    K=1: one bank (= STANDARD). K>1: K banks with disjoint item assignments.
    """
    t0 = time.time()
    try:
        k_active = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_HIPPO)))
        keys_h = _sparse_dg(keys_raw, P_in, k_active)
        vals_h = _sparse_dg(vals_raw, P_in, k_active)

        keys_c_raw = keys_h @ P_hc.t()
        vals_c_raw = vals_h @ P_hc.t()
        keys_c = _l2_normalize(keys_c_raw, dim=1)
        vals_c = _l2_normalize(vals_c_raw, dim=1)

        # Hippo Hebbian write (matches STANDARD path).
        W_h = vals_h.t() @ keys_h

        # Replay phase.
        rng = np.random.RandomState(seed + 17)
        perm_np = rng.permutation(M_ITEMS)
        perm = torch.from_numpy(perm_np).to(DEVICE)
        cues_h = keys_h[perm]
        cues_c = keys_c[perm]

        # Noisy hippo readout (matches STANDARD).
        vals_react_h_raw = cues_h @ W_h.t()
        vals_react_h = torch.sign(vals_react_h_raw)
        vals_react_h = torch.where(vals_react_h == 0,
                                   torch.ones_like(vals_react_h),
                                   vals_react_h)
        vals_c_react_raw = vals_react_h @ P_hc.t()
        vals_c_react = _l2_normalize(vals_c_react_raw, dim=1)

        del W_h, vals_react_h_raw, vals_react_h, vals_c_react_raw
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

        # Compartment write.
        # Each item's bank b_i = perm[i] % K (each ORIGINAL item routes
        # deterministically; ensures different arms have different routing
        # given the same perm).
        original_idx = perm  # the original item index for each replay-position
        bank_assign = original_idx % K_banks  # (M,) bank id per replay-position

        # Build K banks; each W_c_bank[k] = eta * sum_{i: bank_assign[i]==k} vals_c_react[i] outer cues_c[i]
        # Vectorize: for each bank, mask + outer product.
        W_banks: List[torch.Tensor] = []
        bank_sizes: List[int] = []
        for k in range(K_banks):
            mask = (bank_assign == k)
            v_k = vals_c_react[mask]  # (M_k, N_c)
            c_k = cues_c[mask]        # (M_k, N_c)
            bank_sizes.append(int(v_k.shape[0]))
            W_banks.append(ETA_CORTEX * (v_k.t() @ c_k))

        n_total_writes = sum(bank_sizes)

        _heartbeat_write(out_dir, unit_idx=0, total_units=1,
                         elapsed_s=time.time() - t0,
                         extra={"arm": arm_name, "K": K_banks,
                                "bank_sizes": bank_sizes, "seed": int(seed)})

        # Recall: per-query route to its bank, predict, argmax.
        # query item i routes to bank (i % K_banks) for its OWN identity.
        query_banks = torch.arange(M_ITEMS, device=DEVICE) % K_banks
        # For each query, compute pred from its bank.
        preds_n_list = []
        for k in range(K_banks):
            mask = (query_banks == k)
            if mask.any():
                preds_raw = keys_c[mask] @ W_banks[k].t()
                preds = torch.sign(preds_raw)
                preds = torch.where(preds == 0, torch.ones_like(preds), preds)
                preds_n_list.append((mask, _l2_normalize(preds, dim=1)))

        # Assemble full preds_n in correct order.
        preds_n_full = torch.zeros((M_ITEMS, N_CORTEX), dtype=DTYPE, device=DEVICE)
        for mask, pn in preds_n_list:
            preds_n_full[mask] = pn

        sims = preds_n_full @ vals_c.t()
        argmax = torch.argmax(sims, dim=1)
        n_hits = int((argmax == torch.arange(M_ITEMS, device=DEVICE)).sum().item())
        recall = n_hits / float(M_ITEMS)
        cortex_norm = float(sum(torch.linalg.norm(W).item() for W in W_banks))

        arm_hash_val = _arm_hash(arm_name, W_banks)

        del W_banks, preds_n_full, sims, vals_c_react
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "K_banks": int(K_banks),
            "seed": int(seed),
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "bank_sizes": bank_sizes,
            "cortex_norm": float(cortex_norm),
            "n_total_writes": int(n_total_writes),
            "arm_hash": str(arm_hash_val),
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "K_banks": int(K_banks),
            "seed": int(seed),
            "recall_cortex": float("nan"),
            "n_items": 0,
            "bank_sizes": [],
            "cortex_norm": float("nan"),
            "n_total_writes": 0,
            "arm_hash": "ERROR",
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {str(exc)[:200]}",
        }


def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    N_raw = 64
    keys_raw_np = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float32)
    vals_raw_np = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float32)
    rng_p = np.random.RandomState(seed + 1000)
    P_in_np = (rng_p.randn(N_HIPPO, N_raw) / np.sqrt(N_raw)).astype(np.float32)
    P_hc_np = (rng_p.randn(N_CORTEX, N_HIPPO) / np.sqrt(N_HIPPO)).astype(np.float32)

    keys_raw = torch.from_numpy(keys_raw_np).to(DEVICE)
    vals_raw = torch.from_numpy(vals_raw_np).to(DEVICE)
    P_in = torch.from_numpy(P_in_np).to(DEVICE)
    P_hc = torch.from_numpy(P_hc_np).to(DEVICE)

    print(f"  [seed={seed}] M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} "
          f"K_banks={K_BANK_VALUES} dev={DEVICE.type} run_mode={RUN_MODE}",
          flush=True)

    arms = []
    for arm_name, K_banks in zip(ARM_NAMES, K_BANK_VALUES):
        out = run_arm(arm_name, K_banks, seed,
                      keys_raw, vals_raw, P_in, P_hc, out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name:>22s} K={K_banks:>3d}] "
            f"recall={out['recall_cortex']:.3f} "
            f"cortex_norm={out['cortex_norm']:.2e} "
            f"hash={out['arm_hash']} status={out['arm_status'][:30]} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N": N_CORTEX,
        "N_c": N_CORTEX,
        "N_h": N_HIPPO,
        "M": M_ITEMS,
        "n_arms": len(ARM_NAMES),
        "eta_c": ETA_CORTEX,
        "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
        "n_replay_per_item": N_REPLAY_PER_ITEM,
        "backend": "torch",
        "device": DEVICE.type,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "K_bank_values": list(K_BANK_VALUES),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


def _arm_recall_mean(arms_across_seeds: List[List[Dict]], arm_name: str) -> float:
    vals = []
    for seed_arms in arms_across_seeds:
        for a in seed_arms:
            if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                vals.append(float(a["recall_cortex"]))
    return float(np.mean(vals)) if vals else float("nan")


def _arm_hashes(arms_across_seeds: List[List[Dict]], arm_name: str) -> List[str]:
    out = []
    for seed_arms in arms_across_seeds:
        for a in seed_arms:
            if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                out.append(str(a["arm_hash"]))
    return out


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No seed results.")
    if len(results) != len(SEEDS):
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {len(SEEDS)} seeds, got {len(results)}")
    arms_across = []
    for r in results:
        if len(r.get("arms", [])) != len(ARM_NAMES):
            return ("HARD_FAIL",
                    f"CARDINALITY_BREACH: seed={r.get('seed')} has "
                    f"{len(r.get('arms', []))} arms, expected {len(ARM_NAMES)}")
        for a in r["arms"]:
            if a["arm_status"] != "OK":
                return ("HARD_FAIL",
                        f"seed={r['seed']} arm={a['arm_name']} "
                        f"error: {a['arm_status']}")
        arms_across.append(r["arms"])

    # META_RULE_AF arms-must-differ.
    af_violations: List[str] = []
    for i in range(len(ARM_NAMES)):
        for j in range(i + 1, len(ARM_NAMES)):
            a1, a2 = ARM_NAMES[i], ARM_NAMES[j]
            h1, h2 = _arm_hashes(arms_across, a1), _arm_hashes(arms_across, a2)
            any_diff = any(x != y for x, y in zip(h1, h2))
            if not any_diff and h1 and h2:
                af_violations.append(f"{a1}/{a2}")
    if af_violations:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: identical arm_hash across all seeds "
                f"for: {af_violations}")

    R_STANDARD = _arm_recall_mean(arms_across, "ARM_STANDARD_K1")
    arm_recalls = {arm: _arm_recall_mean(arms_across, arm) for arm in ARM_NAMES}

    compartment_arms = [a for a in ARM_NAMES if a != "ARM_STANDARD_K1"]
    best_arm = max(compartment_arms, key=lambda a: arm_recalls[a])
    best_recall = arm_recalls[best_arm]
    best_lift = best_recall - R_STANDARD

    best_K = int(best_arm.replace("ARM_COMPARTMENT_K", ""))

    # Monotonic check: ideally recall climbs with K (smaller per-bank load = better).
    K_swr = [K for K in K_BANK_VALUES if K > 1]
    arm_for_K = {K: f"ARM_COMPARTMENT_K{K}" for K in K_swr}
    is_monotonic = all(
        arm_recalls[arm_for_K[K_swr[i]]] <= arm_recalls[arm_for_K[K_swr[i + 1]]]
        + 0.05
        for i in range(len(K_swr) - 1)
    )

    arm_summary = " ".join(
        f"{arm}={arm_recalls[arm]:.3f}" for arm in ARM_NAMES
    )
    summary = (
        f"M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} alpha_simple="
        f"{_alpha_simple(M_ITEMS, N_HIPPO):.3f} mode={RUN_MODE} "
        f"{arm_summary} | best_K={best_K} best_lift={best_lift:+.3f} "
        f"monotonic={is_monotonic} "
        f"R_STANDARD_K1={R_STANDARD:.3f}"
    )

    if best_lift >= HARD_PASS_LIFT_MIN:
        return ("HARD_PASS",
                f"HARD_PASS (Hc_COMPARTMENT_RESCUE_CONFIRMED): K={best_K} banks "
                f"lifts recall by {best_lift:+.3f} (>= HARD_PASS_LIFT_MIN "
                f"{HARD_PASS_LIFT_MIN}). {summary}")
    if best_lift >= MIDDLE_BAND_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: partial Hc rescue lift {best_lift:+.3f} below "
                f"HARD_PASS threshold {HARD_PASS_LIFT_MIN}. {summary}")
    return ("HARD_FAIL",
            f"HARD_FAIL: compartmentalization does not rescue Hc (best lift "
            f"{best_lift:+.3f} < {MIDDLE_BAND_LIFT_MIN}). {summary}")


def _selftest_sparse_dg() -> None:
    rng = np.random.RandomState(7)
    N_raw = 32
    N_h_test = 128
    k_test = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_test)))
    P_np = (rng.randn(N_h_test, N_raw) / np.sqrt(N_raw)).astype(np.float32)
    x_np = rng.choice([-1.0, 1.0], size=(4, N_raw)).astype(np.float32)
    P = torch.from_numpy(P_np).to(DEVICE)
    x = torch.from_numpy(x_np).to(DEVICE)
    h = _sparse_dg(x, P, k_test)
    active = (h.abs() > 0).sum(dim=1)
    if not (active == k_test).all().item():
        raise AssertionError(
            f"k-WTA sparsity wrong: got {active.cpu().numpy()}, want {k_test}")


def _selftest_K_bank_distinct() -> None:
    if len(set(K_BANK_VALUES)) != len(K_BANK_VALUES):
        raise AssertionError(
            f"K_BANK_VALUES has duplicates: {K_BANK_VALUES}")
    if 1 not in K_BANK_VALUES:
        raise AssertionError("K=1 baseline missing (ARM_STANDARD_K1)")
    # K_banks must divide M cleanly OR at least be reasonable; allow uneven.


def _selftest_arm_count_matches() -> None:
    if len(ARM_NAMES) != len(K_BANK_VALUES):
        raise AssertionError(
            f"ARM_NAMES count {len(ARM_NAMES)} != K_BANK_VALUES count "
            f"{len(K_BANK_VALUES)}")
    expected = len(ARM_NAMES) * len(SEEDS)
    if expected != EXPECTED_N_UNITS:
        raise AssertionError(
            f"EXPECTED_N_UNITS={EXPECTED_N_UNITS} mismatch")


def _selftest_torch_available() -> None:
    if not hasattr(torch, "sign"):
        raise AssertionError("torch.sign missing - bad torch install")


def _selftest_regime_alpha() -> None:
    a_full = _alpha_simple(M_ITEMS_FULL, N_HIPPO_FULL)
    a_smoke = _alpha_simple(M_ITEMS_SMOKE, N_HIPPO_SMOKE)
    if abs(a_full - a_smoke) > 1e-3:
        raise AssertionError(
            f"smoke alpha {a_smoke:.3f} != full alpha {a_full:.3f}: "
            f"discriminator-must-survive-scale violated")
    if not (0.20 < a_full < 0.30):
        raise AssertionError(
            f"alpha_simple={a_full:.3f} not in v2 reference (0.20,0.30)")


def _instrumentation_selftest() -> None:
    try:
        _selftest_torch_available()
        _selftest_sparse_dg()
        _selftest_K_bank_distinct()
        _selftest_arm_count_matches()
        _selftest_regime_alpha()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  M={M_ITEMS}  N_h={N_HIPPO}  N_c={N_CORTEX}  "
        f"K_banks={K_BANK_VALUES}  alpha_simple="
        f"{_alpha_simple(M_ITEMS, N_HIPPO):.3f}  "
        f"seeds={SEEDS}  arms={ARM_NAMES}  device={DEVICE.type}  "
        f"expected_n_units={EXPECTED_N_UNITS}  mode={RUN_MODE}  "
        f"marker={_HARDENING_MARKER}",
        flush=True,
    )


def _write_crash_metrics(output_dir: Path, anchor_name: str,
                         exc: BaseException) -> None:
    diag = {
        "anchor_name": anchor_name,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "run_mode": RUN_MODE,
    }
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        tmp = output_dir / "metrics.json.tmp"
        final = output_dir / "metrics.json"
        tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(final))
    except Exception:
        pass


def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "_start_marker.txt").write_text(
        f"start_ts_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"anchor={ANCHOR_NAME} run_mode={RUN_MODE} device={DEVICE.type} "
        f"K_banks={K_BANK_VALUES}",
        encoding="utf-8",
    )

    try:
        run_config = {
            "N": N_CORTEX, "M": M_ITEMS, "N_h": N_HIPPO, "run_mode": RUN_MODE,
            "anchor": ANCHOR_NAME,
        }
        done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
        print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
              f"running {remaining}", flush=True)

        t_sweep_start = time.time()
        for seed in remaining:
            print(f"[seed={seed}] {ANCHOR_NAME} run_mode={RUN_MODE}...",
                  flush=True)
            result = run_seed(seed, out_dir)
            write_partial(out_dir, seed, result)

        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
        all_results = list(per_seed.values())
        verdict, verdict_msg = compute_verdict(all_results)

        elapsed_s = time.time() - t_sweep_start
        print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
        print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

        mode_in_results = {r.get("run_mode", "?") for r in all_results}
        if RUN_MODE == "full" and "smoke" in mode_in_results:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL: stale smoke partials in FULL run. "
                f"mode_in_results={mode_in_results}. " + verdict_msg
            )

        per_arm_rows: List[Dict] = []
        for arm_name in ARM_NAMES:
            recalls = []
            K_b = None
            for r in all_results:
                for a in r.get("arms", []):
                    if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                        recalls.append(float(a["recall_cortex"]))
                        K_b = a.get("K_banks")
            if recalls:
                per_arm_rows.append({
                    "arm_name": arm_name,
                    "K_banks": K_b,
                    "recall_mean": float(np.mean(recalls)),
                    "recall_std": float(np.std(recalls)) if len(recalls) > 1 else 0.0,
                    "n_seeds_ok": len(recalls),
                })

        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": (
                f"n_seeds={len(all_results)} M={M_ITEMS} N_h={N_HIPPO} "
                f"N_c={N_CORTEX} K_banks={K_BANK_VALUES} mode={RUN_MODE} "
                f"alpha_simple={_alpha_simple(M_ITEMS, N_HIPPO):.3f} "
                f"device={DEVICE.type} compartmentalized_cortex_K_banks"
            ),
            "elapsed_s": float(elapsed_s),
            "config_version": CONFIG_VERSION,
            "M": M_ITEMS,
            "N_c": N_CORTEX,
            "N_h": N_HIPPO,
            "eta_c": ETA_CORTEX,
            "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
            "n_replay_per_item": N_REPLAY_PER_ITEM,
            "backend": "torch",
            "device": DEVICE.type,
            "n_seeds": len(SEEDS),
            "expected_n_units": EXPECTED_N_UNITS,
            "cardinality_ok": (
                len(all_results) == len(SEEDS)
                and all(len(r.get("arms", [])) == len(ARM_NAMES) for r in all_results)
            ),
            "run_mode": RUN_MODE,
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "K_bank_values": list(K_BANK_VALUES),
            "per_arm_rows": per_arm_rows,
            "per_seed": [
                {"seed": r.get("seed"), "elapsed_s": r.get("elapsed_s"),
                 "arms": r.get("arms")}
                for r in all_results
            ],
        }
        metrics_path = out_dir / "metrics.json"
        tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        os.replace(str(tmp_path), str(metrics_path))
        print(f"[metrics] written to {metrics_path}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        _write_crash_metrics(out_dir, ANCHOR_NAME, exc)
        raise


if __name__ == "__main__":
    _main()
