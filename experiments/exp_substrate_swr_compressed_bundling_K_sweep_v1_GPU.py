"""substrate_swr_compressed_bundling_K_sweep_v1_GPU.

Stage 2 NREM rescue cell A. Tests sharp-wave-ripple-style COMPRESSED BUNDLING
during cortex consolidation. Brain: hippocampus emits ~150-250Hz ripples during
NREM3 that transmit compressed sequence-packets to cortex; replay is 10-20x
faster than wake and bundles many items into one event.

CITED@Buzsaki+Foster_replay_NREM_compression_brain_lit:
  ~7-12 items packed per ripple event; cortex receives compressed bundle.

LINEAGE:
  Hippo bottleneck v2 (commit c374d74f) MEASURED@d:/AI/hd-instrument/data/exp_substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2/metrics.json:
    R_DIRECT=0.985, R_STANDARD=0.219, R_NO_HEBBIAN_CROSSTERM=0.612 (Ha confirmed),
    R_CLEAN_VALS_TO_CORTEX=0.985 (Hc confirmed).
  Hebbian cross-term + cortex write-saturation are the two H_OTHER mechanisms.
  SWR-K bundling tests rescue: bundle K items into ONE outer-product write
  (vs 1 item/write). Predicts K* where recall climbs from STANDARD toward
  DIRECT.

HYPOTHESIS:
  THEORETICAL@cortex_write_saturation_scaling: write-saturation grows as
  M total writes; if M_writes_effective = M/K via bundling, saturation
  drops by 1/K factor; recall climbs as K -> K* then degrades when bundle
  noise > write-saturation noise.

ARMS (5; META_RULE_AF arms-must-differ via SHA-256 hash):
  ARM_STANDARD             -- baseline: 1 item per outer-product write (K=1)
                              (reproduces hippo_bottleneck_v2 STANDARD path)
  ARM_SWR_K5               -- bundle K=5 items per outer-product write
  ARM_SWR_K10              -- bundle K=10 items per outer-product write
  ARM_SWR_K20              -- bundle K=20 items per outer-product write
  ARM_SWR_K50              -- bundle K=50 items per outer-product write
  (ARM_DIRECT ceiling reference computed analytically; not a separate arm)

PRE-REG BANDS:
  HARD_PASS: best ARM_SWR_K* >= R_STANDARD + 0.20 AND best K* not endpoint
             (interior peak; demonstrates write-saturation trade-off)
  MIDDLE_BAND: best ARM_SWR_K* in (R_STANDARD+0.05, R_STANDARD+0.20]
  HARD_FAIL: no ARM_SWR_K* >= R_STANDARD + 0.05 (no rescue signal)

REGIME (M=8192, N_h=8192, N_c=2048, alpha_simple=1.0 -- chain-grade overcap
regime where Ha + Hc both fire hard; v2 STANDARD measured 0.219 at
alpha_simple=0.25; at alpha_simple=1.0 STANDARD expected even lower).

SMOKE: M=2048, N_h=2048, N_c=512 (alpha_simple=1.0 preserved); 1 seed.
DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at fixed alpha_simple=1.0 preserves
write-saturation regime; mechanism arm gap survives by construction.

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


ANCHOR_NAME = "substrate_swr_compressed_bundling_K_sweep_v1_GPU"
_HARDENING_MARKER = "v1_SWR_K1_K5_K10_K20_K50"

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


# Config.
# Regime: M=2048, N_h=8192, N_c=2048 — matches hippo_bottleneck v2 (alpha_simple=0.25)
# where v2 measured: R_DIRECT=0.985 R_STANDARD=0.219 R_CLEAN=0.985.
# This is the v2 reference regime; we test whether SWR-K bundling on CLEAN
# vals_c (= CLEAN_VALS_TO_CORTEX) at K>1 lifts above CLEAN_K=1's plateau,
# or stays at 0.985 (no benefit at this M; need higher M for write-sat).
# For full we run at M=8192 (alpha=1.0 vs N_h=8192): heavy write-saturation,
# where reducing write count via K-bundling matters most.
M_ITEMS_FULL = 8192
N_HIPPO_FULL = 8192
N_CORTEX_FULL = 2048
SEEDS_FULL = [7, 17, 23]

M_ITEMS_SMOKE = 2048
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

K_BUNDLE_VALUES: Tuple[int, ...] = (1, 5, 10, 20, 50)
ARM_NAMES: Tuple[str, ...] = tuple(
    f"ARM_SWR_K{k}" if k > 1 else "ARM_STANDARD"
    for k in K_BUNDLE_VALUES
)
EXPECTED_N_UNITS = len(ARM_NAMES) * len(SEEDS)

HARD_PASS_LIFT_MIN = 0.20
MIDDLE_BAND_LIFT_MIN = 0.05


def _alpha_simple(M: int, N_h: int) -> float:
    return float(M) / float(N_h)


def _select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


DEVICE = _select_device()
DTYPE = torch.float32  # complex multiplication not used here; float32 sufficient

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},M={M_ITEMS},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"alpha_simple={_alpha_simple(M_ITEMS, N_HIPPO):.3f},"
    f"K_BUNDLE={K_BUNDLE_VALUES},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},DEVICE={DEVICE.type},"
    f"hardening=METARULE_AF+METARULE_AH+METARULE_H+SWR_K_SWEEP"
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
    """Batched k-WTA sparse pattern separator. x:(M,N_raw), P:(N_h,N_raw)."""
    h_raw = x @ P.t()  # (M, N_h)
    abs_h = h_raw.abs()
    topk_idx = torch.topk(abs_h, k, dim=1, largest=True).indices  # (M, k)
    signs = torch.sign(h_raw.gather(1, topk_idx))
    signs = torch.where(signs == 0, torch.ones_like(signs), signs)
    out = torch.zeros_like(h_raw)
    out.scatter_(1, topk_idx, signs)
    return out


def _arm_hash(arm_name: str, W_cortex: torch.Tensor) -> str:
    """Stable hash on deterministic W_cortex sub-slice.

    Hashes W_cortex (not vals_c_react) because all arms share the same hippo
    readout pipeline; the discriminator IS the bundling difference, which
    affects W_cortex but leaves vals_c_react identical.
    """
    sample = W_cortex[:4, :64].detach().cpu().to(torch.float64).numpy()
    return hashlib.sha256(sample.tobytes()).hexdigest()[:16]


def run_arm(arm_name: str, K_bundle: int, seed: int,
            keys_raw: torch.Tensor, vals_raw: torch.Tensor,
            P_in: torch.Tensor, P_hc: torch.Tensor,
            out_dir: Path) -> Dict:
    """One arm: SWR-style compressed CLEAN bundling with K items per write.

    BRAIN-MECHANISM MODEL: SWR is hippocampus emitting clean re-extracted
    sequence packets to cortex (NOT a noisy Hebbian readback). We model SWR
    as CLEAN vals_c[perm] = oracle-extracted item (the v2 CLEAN_VALS_TO_CORTEX
    arm, which v2 measured at R_CLEAN=0.985 vs R_STANDARD=0.219 with K=1).

    The question this cell asks: does BUNDLING K clean items into ONE
    outer-product write LIFT recall above the K=1 clean baseline at heavier
    write-saturation regimes (full M=8192 = alpha=1.0)?

    Pipeline:
      1. Encode keys/vals via sparse-DG -> keys_h, vals_h
      2. Project to cortex: keys_c, vals_c (CLEAN)
      3. SWR bundling: group M items into ceil(M/K) bundles; each bundle write
         is ONE outer product: sum_bundle(vals_c[perm]) outer sum_bundle(cues_c).
      4. Recall: preds = sign(keys_c @ W_c.T); argmax vs identity.

    K=1 reproduces STANDARD (1 clean item per write = v2 CLEAN_VALS_TO_CORTEX);
    K>1 is SWR-bundled (compression). Brain bundles ~7-12 items per ripple.
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

        # Replay phase: clean re-extraction (SWR model).
        rng = np.random.RandomState(seed + 17)
        perm = torch.from_numpy(rng.permutation(M_ITEMS)).to(DEVICE)
        cues_c = keys_c[perm]
        vals_c_perm = vals_c[perm]

        # SWR bundling: group M items into ceil(M/K) bundles.
        # Each bundle write: W_c += eta * sum_bundle(vals_c_perm) outer sum_bundle(cues_c)
        # Vectorized: reshape -> view -> sum across K axis -> batched outer product.
        n_bundles = math.ceil(M_ITEMS / K_bundle)
        # Pad to make divisible.
        pad = n_bundles * K_bundle - M_ITEMS
        if pad > 0:
            zero_pad_v = torch.zeros((pad, N_CORTEX), dtype=DTYPE, device=DEVICE)
            zero_pad_c = torch.zeros((pad, N_CORTEX), dtype=DTYPE, device=DEVICE)
            vals_c_padded = torch.cat([vals_c_perm, zero_pad_v], dim=0)
            cues_c_padded = torch.cat([cues_c, zero_pad_c], dim=0)
        else:
            vals_c_padded = vals_c_perm
            cues_c_padded = cues_c

        vals_bundled = vals_c_padded.view(n_bundles, K_bundle, N_CORTEX).sum(dim=1)
        cues_bundled = cues_c_padded.view(n_bundles, K_bundle, N_CORTEX).sum(dim=1)

        # W_cortex accumulates n_bundles outer products.
        # W_c = eta * vals_bundled.T @ cues_bundled
        W_cortex = ETA_CORTEX * (vals_bundled.t() @ cues_bundled)
        n_total_writes = n_bundles

        _heartbeat_write(out_dir, unit_idx=0, total_units=1,
                         elapsed_s=time.time() - t0,
                         extra={"arm": arm_name, "K": K_bundle,
                                "n_bundles": n_bundles, "seed": int(seed)})

        # Recall.
        preds_raw = keys_c @ W_cortex.t()
        preds = torch.sign(preds_raw)
        preds = torch.where(preds == 0, torch.ones_like(preds), preds)
        preds_n = _l2_normalize(preds, dim=1)
        sims = preds_n @ vals_c.t()
        argmax = torch.argmax(sims, dim=1)
        n_hits = int((argmax == torch.arange(M_ITEMS, device=DEVICE)).sum().item())
        recall = n_hits / float(M_ITEMS)
        cortex_norm = float(torch.linalg.norm(W_cortex).item())

        arm_hash_val = _arm_hash(arm_name, W_cortex)

        # Free intermediates.
        del W_cortex, preds_raw, preds, preds_n, sims, vals_bundled, cues_bundled
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "K_bundle": int(K_bundle),
            "seed": int(seed),
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "n_bundles": int(n_bundles),
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
            "K_bundle": int(K_bundle),
            "seed": int(seed),
            "recall_cortex": float("nan"),
            "n_items": 0,
            "n_bundles": 0,
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
          f"K_values={K_BUNDLE_VALUES} dev={DEVICE.type} run_mode={RUN_MODE}",
          flush=True)

    arms = []
    for arm_name, K_bundle in zip(ARM_NAMES, K_BUNDLE_VALUES):
        out = run_arm(arm_name, K_bundle, seed,
                      keys_raw, vals_raw, P_in, P_hc, out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name:>16s} K={K_bundle:>3d}] "
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
        "K_bundle_values": list(K_BUNDLE_VALUES),
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

    # META_RULE_AF arms-must-differ: all pairs distinct hash on at least one seed.
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

    R_STANDARD = _arm_recall_mean(arms_across, "ARM_STANDARD")
    arm_recalls = {arm: _arm_recall_mean(arms_across, arm) for arm in ARM_NAMES}

    # Best SWR arm (excluding STANDARD).
    swr_arms = [a for a in ARM_NAMES if a != "ARM_STANDARD"]
    best_arm = max(swr_arms, key=lambda a: arm_recalls[a])
    best_recall = arm_recalls[best_arm]
    best_lift = best_recall - R_STANDARD

    # Interior peak check: best K is not the smallest or largest in sweep.
    best_K = int(best_arm.replace("ARM_SWR_K", ""))
    K_swr = [K for K in K_BUNDLE_VALUES if K > 1]
    is_interior = (best_K != min(K_swr)) and (best_K != max(K_swr))

    arm_summary = " ".join(
        f"{arm}={arm_recalls[arm]:.3f}" for arm in ARM_NAMES
    )
    summary = (
        f"M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} alpha_simple="
        f"{_alpha_simple(M_ITEMS, N_HIPPO):.3f} mode={RUN_MODE} "
        f"{arm_summary} | best_K={best_K} best_lift={best_lift:+.3f} "
        f"interior_peak={is_interior}"
    )

    if best_lift >= HARD_PASS_LIFT_MIN and is_interior:
        return ("HARD_PASS",
                f"HARD_PASS (SWR_K_RESCUE_CONFIRMED): best K={best_K} lifts "
                f"recall by {best_lift:+.3f} over STANDARD with interior peak "
                f"(write-saturation trade-off demonstrated). {summary}")
    if best_lift >= HARD_PASS_LIFT_MIN and not is_interior:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: best K={best_K} lifts recall but at sweep endpoint "
                f"(no interior trade-off; mechanism may be monotonic in K). {summary}")
    if best_lift >= MIDDLE_BAND_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: partial lift {best_lift:+.3f} below HARD_PASS "
                f"threshold {HARD_PASS_LIFT_MIN}. {summary}")
    return ("HARD_FAIL",
            f"HARD_FAIL: no SWR-K rescue (best lift {best_lift:+.3f} < "
            f"{MIDDLE_BAND_LIFT_MIN}). {summary}")


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


def _selftest_K_sweep_distinct() -> None:
    """At smoke regime, the 5 K-bundle arms must produce distinct vals_c_react
    bundling structures => distinct W_cortex (different recall expected)."""
    if len(set(K_BUNDLE_VALUES)) != len(K_BUNDLE_VALUES):
        raise AssertionError(
            f"K_BUNDLE_VALUES has duplicates: {K_BUNDLE_VALUES}")
    if 1 not in K_BUNDLE_VALUES:
        raise AssertionError("K=1 baseline missing (ARM_STANDARD)")


def _selftest_arm_count_matches() -> None:
    if len(ARM_NAMES) != len(K_BUNDLE_VALUES):
        raise AssertionError(
            f"ARM_NAMES count {len(ARM_NAMES)} != K_BUNDLE_VALUES count "
            f"{len(K_BUNDLE_VALUES)}")
    expected = len(ARM_NAMES) * len(SEEDS)
    if expected != EXPECTED_N_UNITS:
        raise AssertionError(
            f"EXPECTED_N_UNITS={EXPECTED_N_UNITS} mismatch")


def _selftest_torch_available() -> None:
    # GPU queue routing requires torch; sanity that import works
    if not hasattr(torch, "sign"):
        raise AssertionError("torch.sign missing - bad torch install")


def _selftest_regime_alpha() -> None:
    a_full = _alpha_simple(M_ITEMS_FULL, N_HIPPO_FULL)
    a_smoke = _alpha_simple(M_ITEMS_SMOKE, N_HIPPO_SMOKE)
    if abs(a_full - a_smoke) > 1e-3:
        raise AssertionError(
            f"smoke alpha {a_smoke:.3f} != full alpha {a_full:.3f}: "
            f"discriminator-must-survive-scale violated")


def _instrumentation_selftest() -> None:
    try:
        _selftest_torch_available()
        _selftest_sparse_dg()
        _selftest_K_sweep_distinct()
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
        f"K_values={K_BUNDLE_VALUES}  alpha_simple="
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
        f"K_values={K_BUNDLE_VALUES}",
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
                        K_b = a.get("K_bundle")
            if recalls:
                per_arm_rows.append({
                    "arm_name": arm_name,
                    "K_bundle": K_b,
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
                f"N_c={N_CORTEX} K_values={K_BUNDLE_VALUES} mode={RUN_MODE} "
                f"alpha_simple={_alpha_simple(M_ITEMS, N_HIPPO):.3f} "
                f"device={DEVICE.type} SWR_compressed_bundling_K_sweep"
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
            "K_bundle_values": list(K_BUNDLE_VALUES),
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
